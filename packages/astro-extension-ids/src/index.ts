import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import type { AstroIntegration } from "astro";

type ExtensionIdKind = "text" | "icon" | "image";
type EveRefKind = "icon" | "localization" | "type";

interface ExtensionIdEntry {
    component: string;
    file: string;
    id: string;
    kind: ExtensionIdKind;
    line: number;
}

interface ExtensionIdUnresolved {
    component: string;
    expectedProp: string;
    file: string;
    line: number;
}

interface EveRefEntry {
    component: string;
    file: string;
    id: number;
    kind: EveRefKind;
    line: number;
    prop: string;
}

interface EveRefUnresolved {
    component: string;
    expectedProp: string;
    file: string;
    kind: EveRefKind;
    line: number;
}

interface ExtensionIdManifest {
    duplicates: Array<{
        id: string;
        occurrences: Array<{
            component: string;
            file: string;
            kind: ExtensionIdKind;
            line: number;
        }>;
    }>;
    entries: ExtensionIdEntry[];
    eveRefs: {
        duplicates: Array<{
            id: number;
            kind: EveRefKind;
            occurrences: Array<{
                component: string;
                file: string;
                line: number;
                prop: string;
            }>;
        }>;
        entries: EveRefEntry[];
        iconIds: number[];
        locIds: number[];
        typeIds: number[];
        unresolved: EveRefUnresolved[];
    };
    generatedAt: string;
    unresolved: ExtensionIdUnresolved[];
}

interface ExtensionIdSpec {
    component: string;
    kind: ExtensionIdKind;
    prop: string;
}

interface EveRefSpec {
    component: string;
    kind: EveRefKind;
    prop: string;
}

interface ExtensionIdsIntegrationOptions {
    outputFile?: string;
}

interface MdxJsxAttributeValueExpression {
    type: "mdxJsxAttributeValueExpression";
    value: string;
}

interface MdxJsxAttribute {
    name: string;
    type: "mdxJsxAttribute";
    value?: MdxJsxAttributeValueExpression | null | string;
}

interface MdxJsxExpressionAttribute {
    type: "mdxJsxExpressionAttribute";
}

interface MdxJsxElement {
    attributes?: Array<MdxJsxAttribute | MdxJsxExpressionAttribute>;
    children?: unknown[];
    name?: string | null;
    position?: {
        start?: {
            line?: number | null;
        };
    };
    type: "mdxJsxFlowElement" | "mdxJsxTextElement";
}

const componentSpecs: ExtensionIdSpec[] = [
    {
        component: "LocalizedText",
        kind: "text",
        prop: "id",
    },
    {
        component: "LocalizedIconText",
        kind: "text",
        prop: "id",
    },
    {
        component: "LocalizedIconText",
        kind: "icon",
        prop: "iconId",
    },
    {
        component: "InlineIcon",
        kind: "icon",
        prop: "id",
    },
    {
        component: "InlineImage",
        kind: "image",
        prop: "id",
    },
];

const eveRefSpecs: EveRefSpec[] = [
    {
        component: "EveType",
        kind: "type",
        prop: "typeId",
    },
    {
        component: "EveLocText",
        kind: "localization",
        prop: "locId",
    },
    {
        component: "EveIcon",
        kind: "icon",
        prop: "iconId",
    },
];

class ExtensionIdCollector {
    #byFile = new Map<
        string,
        {
            entries: ExtensionIdEntry[];
            eveEntries: EveRefEntry[];
            eveUnresolved: EveRefUnresolved[];
            unresolved: ExtensionIdUnresolved[];
        }
    >();
    #outputFile: string;
    #rootDir: string;

    constructor(rootDir: string, outputFile: string) {
        this.#rootDir = rootDir;
        this.#outputFile = outputFile;
    }

    clear() {
        this.#byFile.clear();
    }

    recordFile(
        filePath: string,
        entries: ExtensionIdEntry[],
        unresolved: ExtensionIdUnresolved[],
        eveEntries: EveRefEntry[],
        eveUnresolved: EveRefUnresolved[],
    ) {
        this.#byFile.set(filePath, {
            entries,
            eveEntries,
            eveUnresolved,
            unresolved,
        });
    }

    buildManifest(): ExtensionIdManifest {
        const entries = [...this.#byFile.values()]
            .flatMap((value) => value.entries)
            .sort(compareEntries);
        const unresolved = [...this.#byFile.values()]
            .flatMap((value) => value.unresolved)
            .sort(compareUnresolved);
        const eveEntries = [...this.#byFile.values()]
            .flatMap((value) => value.eveEntries)
            .sort(compareEveEntries);
        const eveUnresolved = [...this.#byFile.values()]
            .flatMap((value) => value.eveUnresolved)
            .sort(compareEveUnresolved);

        return {
            duplicates: collectDuplicates(entries),
            entries,
            eveRefs: {
                duplicates: collectEveDuplicates(eveEntries),
                entries: eveEntries,
                iconIds: collectEveIdList(eveEntries, "icon"),
                locIds: collectEveIdList(eveEntries, "localization"),
                typeIds: collectEveIdList(eveEntries, "type"),
                unresolved: eveUnresolved,
            },
            generatedAt: new Date().toISOString(),
            unresolved,
        };
    }

    async writeManifest() {
        const manifest = this.buildManifest();

        await mkdir(path.dirname(this.#outputFile), { recursive: true });
        await writeFile(
            this.#outputFile,
            `${JSON.stringify(manifest, null, 4)}\n`,
            "utf8",
        );
    }

    outputPathLabel() {
        return normalizeSlashes(path.relative(this.#rootDir, this.#outputFile));
    }
}

function normalizeSlashes(value: string) {
    return value.replaceAll("\\", "/");
}

function compareEntries(left: ExtensionIdEntry, right: ExtensionIdEntry) {
    return (
        left.id.localeCompare(right.id) ||
        left.file.localeCompare(right.file) ||
        left.line - right.line
    );
}

function compareEveEntries(left: EveRefEntry, right: EveRefEntry) {
    return (
        left.kind.localeCompare(right.kind) ||
        left.id - right.id ||
        left.file.localeCompare(right.file) ||
        left.line - right.line ||
        left.prop.localeCompare(right.prop)
    );
}

function compareUnresolved(
    left: ExtensionIdUnresolved,
    right: ExtensionIdUnresolved,
) {
    return (
        left.file.localeCompare(right.file) ||
        left.line - right.line ||
        left.component.localeCompare(right.component) ||
        left.expectedProp.localeCompare(right.expectedProp)
    );
}

function compareEveUnresolved(left: EveRefUnresolved, right: EveRefUnresolved) {
    return (
        left.file.localeCompare(right.file) ||
        left.line - right.line ||
        left.component.localeCompare(right.component) ||
        left.kind.localeCompare(right.kind) ||
        left.expectedProp.localeCompare(right.expectedProp)
    );
}

function collectDuplicates(entries: ExtensionIdEntry[]) {
    const byId = new Map<
        string,
        ExtensionIdManifest["duplicates"][number]["occurrences"]
    >();

    for (const entry of entries) {
        const bucket = byId.get(entry.id) ?? [];
        bucket.push({
            component: entry.component,
            file: entry.file,
            kind: entry.kind,
            line: entry.line,
        });
        byId.set(entry.id, bucket);
    }

    return [...byId.entries()]
        .filter(([, occurrences]) => occurrences.length > 1)
        .map(([id, occurrences]) => ({
            id,
            occurrences,
        }))
        .sort((left, right) => left.id.localeCompare(right.id));
}

function collectEveDuplicates(entries: EveRefEntry[]) {
    const byRef = new Map<
        string,
        ExtensionIdManifest["eveRefs"]["duplicates"][number]
    >();

    for (const entry of entries) {
        const key = `${entry.kind}:${entry.id}`;
        const bucket = byRef.get(key) ?? {
            id: entry.id,
            kind: entry.kind,
            occurrences: [],
        };

        bucket.occurrences.push({
            component: entry.component,
            file: entry.file,
            line: entry.line,
            prop: entry.prop,
        });
        byRef.set(key, bucket);
    }

    return [...byRef.values()]
        .filter((entry) => entry.occurrences.length > 1)
        .sort(
            (left, right) =>
                left.kind.localeCompare(right.kind) || left.id - right.id,
        );
}

function collectEveIdList(entries: EveRefEntry[], kind: EveRefKind) {
    return [
        ...new Set(
            entries
                .filter((entry) => entry.kind === kind)
                .map((entry) => entry.id),
        ),
    ].sort((left, right) => left - right);
}

function isMdxJsxElement(node: unknown): node is MdxJsxElement {
    return (
        typeof node === "object" &&
        node !== null &&
        "type" in node &&
        (node.type === "mdxJsxFlowElement" || node.type === "mdxJsxTextElement")
    );
}

function isMdxJsxAttribute(
    attribute: MdxJsxAttribute | MdxJsxExpressionAttribute,
): attribute is MdxJsxAttribute {
    return attribute.type === "mdxJsxAttribute";
}

function unwrapQuotedLiteral(rawValue: string): string | null {
    const quote = rawValue.at(0);
    const lastQuote = rawValue.at(-1);

    if (
        quote &&
        lastQuote === quote &&
        (quote === '"' || quote === "'" || quote === "`")
    ) {
        return rawValue.slice(1, -1);
    }

    return null;
}

function parseLiteralString(value: MdxJsxAttribute["value"]): string | null {
    if (typeof value === "string") {
        return value;
    }

    if (!value || value.type !== "mdxJsxAttributeValueExpression") {
        return null;
    }

    return unwrapQuotedLiteral(value.value.trim());
}

function parseLiteralInteger(value: MdxJsxAttribute["value"]): number | null {
    const rawValue =
        typeof value === "string" ? value.trim() : value?.value.trim();

    if (!rawValue) {
        return null;
    }

    const unwrappedValue = unwrapQuotedLiteral(rawValue)?.trim() ?? rawValue;

    if (!/^-?\d+$/.test(unwrappedValue)) {
        return null;
    }

    const parsedValue = Number(unwrappedValue);

    if (!Number.isSafeInteger(parsedValue)) {
        return null;
    }

    return parsedValue;
}

function getAttributeValue(node: MdxJsxElement, propName: string) {
    return node.attributes
        ?.filter(isMdxJsxAttribute)
        .find((candidate) => candidate.name === propName)?.value;
}

function getLiteralAttributeValue(
    node: MdxJsxElement,
    propName: string,
): string | null {
    return parseLiteralString(getAttributeValue(node, propName));
}

function getLiteralIntegerAttributeValue(
    node: MdxJsxElement,
    propName: string,
): number | null {
    return parseLiteralInteger(getAttributeValue(node, propName));
}

function getLineNumber(node: MdxJsxElement) {
    return node.position?.start?.line ?? 1;
}

function visitMdxJsxElements(
    tree: unknown,
    visitor: (node: MdxJsxElement) => void,
) {
    const queue: unknown[] = [tree];

    while (queue.length > 0) {
        const currentNode = queue.pop();

        if (!currentNode || typeof currentNode !== "object") {
            continue;
        }

        if (isMdxJsxElement(currentNode)) {
            visitor(currentNode);
        }

        if ("children" in currentNode && Array.isArray(currentNode.children)) {
            for (
                let index = currentNode.children.length - 1;
                index >= 0;
                index -= 1
            ) {
                queue.push(currentNode.children[index]);
            }
        }
    }
}

function createRemarkExtensionIdPlugin(
    collector: ExtensionIdCollector,
    rootDir: string,
) {
    return function remarkExtensionIdPlugin() {
        return function transform(
            tree: unknown,
            file: { history: string[]; path?: string },
        ) {
            const absolutePath = file.path ?? file.history[0];

            if (!absolutePath) {
                return;
            }

            const relativeFile = normalizeSlashes(
                path.relative(rootDir, absolutePath),
            );
            const entries: ExtensionIdEntry[] = [];
            const unresolved: ExtensionIdUnresolved[] = [];
            const eveEntries: EveRefEntry[] = [];
            const eveUnresolved: EveRefUnresolved[] = [];

            visitMdxJsxElements(tree, (node) => {
                if (!isMdxJsxElement(node) || !node.name) {
                    return;
                }

                for (const spec of componentSpecs) {
                    if (node.name !== spec.component) {
                        continue;
                    }

                    const literalValue = getLiteralAttributeValue(
                        node,
                        spec.prop,
                    );
                    const line = getLineNumber(node);

                    if (!literalValue) {
                        unresolved.push({
                            component: spec.component,
                            expectedProp: spec.prop,
                            file: relativeFile,
                            line,
                        });
                        continue;
                    }

                    entries.push({
                        component: spec.component,
                        file: relativeFile,
                        id: literalValue,
                        kind: spec.kind,
                        line,
                    });
                }

                for (const spec of eveRefSpecs) {
                    if (node.name !== spec.component) {
                        continue;
                    }

                    const literalValue = getLiteralIntegerAttributeValue(
                        node,
                        spec.prop,
                    );
                    const line = getLineNumber(node);

                    if (literalValue === null) {
                        eveUnresolved.push({
                            component: spec.component,
                            expectedProp: spec.prop,
                            file: relativeFile,
                            kind: spec.kind,
                            line,
                        });
                        continue;
                    }

                    eveEntries.push({
                        component: spec.component,
                        file: relativeFile,
                        id: literalValue,
                        kind: spec.kind,
                        line,
                        prop: spec.prop,
                    });
                }
            });

            collector.recordFile(
                relativeFile,
                entries,
                unresolved,
                eveEntries,
                eveUnresolved,
            );
        };
    };
}

export default function extensionIdsIntegration(
    options: ExtensionIdsIntegrationOptions = {},
): AstroIntegration {
    let collector: ExtensionIdCollector | undefined;

    return {
        name: "@eve-exploration-guide/astro-extension-ids",
        hooks: {
            "astro:config:setup"({ config, updateConfig }) {
                const rootDir = fileURLToPath(config.root);
                const outputFile = path.resolve(
                    rootDir,
                    options.outputFile ?? "src/generated/extension-ids.json",
                );

                collector = new ExtensionIdCollector(rootDir, outputFile);

                updateConfig({
                    markdown: {
                        remarkPlugins: [
                            createRemarkExtensionIdPlugin(collector, rootDir),
                        ],
                    },
                });
            },
            "astro:build:start"() {
                collector?.clear();
            },
            async "astro:build:done"({ logger }) {
                if (!collector) {
                    return;
                }

                await collector.writeManifest();
                logger.info(
                    `Wrote extension ID manifest to ${collector.outputPathLabel()}`,
                );
            },
        },
    };
}
