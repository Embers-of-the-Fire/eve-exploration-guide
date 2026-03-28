import { spawn } from "node:child_process";

const [mode, ...rawForwardedArgs] = process.argv.slice(2);
const forwardedArgs =
    rawForwardedArgs[0] === "--" ? rawForwardedArgs.slice(1) : rawForwardedArgs;

function runCommand(command, args) {
    return new Promise((resolve, reject) => {
        const child = spawn(command, args, {
            stdio: "inherit",
        });

        child.on("error", reject);
        child.on("exit", (code, signal) => {
            if (signal) {
                reject(new Error(`${command} exited with signal ${signal}`));
                return;
            }

            if (code !== 0) {
                reject(new Error(`${command} exited with code ${code}`));
                return;
            }

            resolve();
        });
    });
}

function getGenerateCommand() {
    if (forwardedArgs.length === 0) {
        return ["pnpm", ["run", "generate:eve-docs-data"]];
    }

    return ["pnpm", ["run", "generate:eve-docs-data", ...forwardedArgs]];
}

async function main() {
    const generateCommand = getGenerateCommand();
    const commandGroups = {
        "build-all": [
            ["pnpm", ["run", "build:collect"]],
            generateCommand,
            ["pnpm", ["run", "build:render"]],
        ],
        "generate-all": [["pnpm", ["run", "build:collect"]], generateCommand],
    };
    const commandGroup = commandGroups[mode];

    if (!commandGroup) {
        throw new Error(`Unsupported eve build pipeline mode: ${mode}`);
    }

    for (const [command, args] of commandGroup) {
        await runCommand(command, args);
    }
}

main().catch((error) => {
    console.error(error instanceof Error ? error.message : String(error));
    process.exitCode = 1;
});
