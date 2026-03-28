import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import type { AstroIntegration } from "astro";
import {
    buildExtensionIdManifest,
    clearExtensionIdCollection,
    setExtensionIdCollectionEnabled,
} from "./runtime";

interface ExtensionIdsIntegrationOptions {
    outputFile?: string;
}

interface MdxJsxAttribute {
    name: string;
    type: "mdxJsxAttribute";
    value?: null | string;
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

const extensionIdMetaFileProp = "__extensionIdFile";
const extensionIdMetaLineProp = "__extensionIdLine";
const instrumentedComponents = new Set([
    "EveFit",
    "EveIcon",
    "EveLocText",
    "EveType",
    "InlineIcon",
    "InlineImage",
    "LocalizedIconText",
    "LocalizedText",
]);

function normalizeSlashes(value: string) {
    return value.replaceAll("\\", "/");
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

function getLineNumber(node: MdxJsxElement) {
    return node.position?.start?.line ?? 1;
}

function injectExtensionIdMetadata(
    node: MdxJsxElement,
    relativeFile: string,
    line: number,
) {
    const attributes = (node.attributes ?? []).filter(
        (attribute) =>
            !(
                isMdxJsxAttribute(attribute) &&
                (attribute.name === extensionIdMetaFileProp ||
                    attribute.name === extensionIdMetaLineProp)
            ),
    );

    attributes.push({
        name: extensionIdMetaFileProp,
        type: "mdxJsxAttribute",
        value: relativeFile,
    });

    attributes.push({
        name: extensionIdMetaLineProp,
        type: "mdxJsxAttribute",
        value: String(line),
    });

    node.attributes = attributes;
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

function createExtensionIdMetadataPlugin(rootDir: string) {
    return function extensionIdMetadataPlugin() {
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

            visitMdxJsxElements(tree, (node) => {
                if (!node.name || !instrumentedComponents.has(node.name)) {
                    return;
                }

                injectExtensionIdMetadata(
                    node,
                    relativeFile,
                    getLineNumber(node),
                );
            });
        };
    };
}

function isCollectMode() {
    return process.env.EXTENSION_IDS_MODE === "collect";
}

export default function extensionIdsIntegration(
    options: ExtensionIdsIntegrationOptions = {},
): AstroIntegration {
    let outputFile: string | undefined;

    return {
        name: "@eve-exploration-guide/astro-extension-ids",
        hooks: {
            "astro:config:setup"({ config, updateConfig }) {
                const rootDir = fileURLToPath(config.root);

                outputFile = path.resolve(
                    rootDir,
                    options.outputFile ?? "src/generated/extension-ids.json",
                );

                updateConfig({
                    markdown: {
                        remarkPlugins: [
                            createExtensionIdMetadataPlugin(rootDir),
                        ],
                    },
                });
            },
            "astro:build:start"() {
                clearExtensionIdCollection();
                setExtensionIdCollectionEnabled(isCollectMode());
            },
            async "astro:build:done"({ logger }) {
                const collectMode = isCollectMode();

                setExtensionIdCollectionEnabled(false);

                if (!collectMode || !outputFile) {
                    return;
                }

                const manifest = buildExtensionIdManifest();

                await mkdir(path.dirname(outputFile), { recursive: true });
                await writeFile(
                    outputFile,
                    `${JSON.stringify(manifest, null, 4)}\n`,
                    "utf8",
                );
                logger.info(
                    `Wrote extension ID manifest to ${normalizeSlashes(
                        path.relative(process.cwd(), outputFile),
                    )}`,
                );
            },
        },
    };
}
