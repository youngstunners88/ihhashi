/**
 * context.ts — Codebase Context Provider for iHhashi Swarm
 *
 * Auto-generates structured context snapshots from the iHhashi codebase.
 * Agents receive only their relevant context slice to keep token costs low.
 */

import { readdir, readFile, writeFile, mkdir } from "fs/promises";
import { join, relative } from "path";
import { getAgent, type AgentInfo } from "./hierarchy";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface RouteInfo {
  file: string;
  prefix: string;
  endpoints: string[];
  lineCount: number;
}

export interface ModelInfo {
  file: string;
  name: string;
  fields: string[];
  lineCount: number;
}

export interface ComponentInfo {
  file: string;
  name: string;
  type: "page" | "component" | "hook" | "service";
}

export interface BackendMap {
  generatedAt: string;
  routes: RouteInfo[];
  models: ModelInfo[];
  services: string[];
}

export interface FrontendMap {
  generatedAt: string;
  pages: ComponentInfo[];
  components: ComponentInfo[];
  hooks: ComponentInfo[];
  services: ComponentInfo[];
}

export interface ApiSurface {
  generatedAt: string;
  totalEndpoints: number;
  routeModules: { name: string; file: string; endpointCount: number }[];
}

// ---------------------------------------------------------------------------
// Backend Map Generator
// ---------------------------------------------------------------------------

export async function generateBackendMap(projectRoot: string): Promise<BackendMap> {
  const routesDir = join(projectRoot, "backend/app/routes");
  const modelsDir = join(projectRoot, "backend/app/models");
  const servicesDir = join(projectRoot, "backend/app/services");
  const contextDir = join(projectRoot, "swarm/context");

  await mkdir(contextDir, { recursive: true });

  // Parse routes
  const routes: RouteInfo[] = [];
  try {
    const routeFiles = await readdir(routesDir);
    for (const file of routeFiles) {
      if (!file.endsWith(".py") || file === "__init__.py") continue;
      const content = await readFile(join(routesDir, file), "utf-8");
      const lines = content.split("\n");
      const endpoints = lines
        .filter((l) => /^\s*@router\.(get|post|put|delete|patch|websocket)/i.test(l))
        .map((l) => l.trim());
      const prefixMatch = content.match(/prefix\s*=\s*["']([^"']+)["']/);
      routes.push({
        file: `backend/app/routes/${file}`,
        prefix: prefixMatch?.[1] || `/${file.replace(".py", "")}`,
        endpoints,
        lineCount: lines.length,
      });
    }
  } catch {
    // Routes dir may not exist
  }

  // Parse models
  const models: ModelInfo[] = [];
  try {
    const modelFiles = await readdir(modelsDir);
    for (const file of modelFiles) {
      if (!file.endsWith(".py") || file === "__init__.py") continue;
      const content = await readFile(join(modelsDir, file), "utf-8");
      const lines = content.split("\n");
      const classMatch = content.match(/class\s+(\w+)\s*\(/);
      const fields = lines
        .filter((l) => /^\s+\w+\s*[:=]/.test(l) && !/^\s*(def|class|#|@)/.test(l))
        .map((l) => l.trim().split(/[:=]/)[0].trim())
        .filter((f) => f.length > 0 && !f.startsWith("_"));
      models.push({
        file: `backend/app/models/${file}`,
        name: classMatch?.[1] || file.replace(".py", ""),
        fields: fields.slice(0, 20), // Limit to 20 fields
        lineCount: lines.length,
      });
    }
  } catch {
    // Models dir may not exist
  }

  // List services
  const services: string[] = [];
  try {
    const serviceFiles = await readdir(servicesDir);
    for (const file of serviceFiles) {
      if (file.endsWith(".py") && file !== "__init__.py") {
        services.push(`backend/app/services/${file}`);
      }
    }
  } catch {
    // Services dir may not exist
  }

  const map: BackendMap = {
    generatedAt: new Date().toISOString(),
    routes,
    models,
    services,
  };

  await writeFile(join(contextDir, "backend-map.json"), JSON.stringify(map, null, 2));
  return map;
}

// ---------------------------------------------------------------------------
// Frontend Map Generator
// ---------------------------------------------------------------------------

export async function generateFrontendMap(projectRoot: string): Promise<FrontendMap> {
  const srcDir = join(projectRoot, "frontend/src");
  const contextDir = join(projectRoot, "swarm/context");

  await mkdir(contextDir, { recursive: true });

  async function scanDir(dir: string, type: ComponentInfo["type"]): Promise<ComponentInfo[]> {
    const items: ComponentInfo[] = [];
    try {
      const files = await readdir(dir);
      for (const file of files) {
        if (file.endsWith(".tsx") || file.endsWith(".ts")) {
          items.push({
            file: relative(projectRoot, join(dir, file)),
            name: file.replace(/\.(tsx?|jsx?)$/, ""),
            type,
          });
        }
      }
    } catch {
      // Dir may not exist
    }
    return items;
  }

  const pages = await scanDir(join(srcDir, "pages"), "page");
  const components = await scanDir(join(srcDir, "components"), "component");
  const hooks = await scanDir(join(srcDir, "hooks"), "hook");
  const services = await scanDir(join(srcDir, "services"), "service");

  const map: FrontendMap = {
    generatedAt: new Date().toISOString(),
    pages,
    components,
    hooks,
    services,
  };

  await writeFile(join(contextDir, "frontend-map.json"), JSON.stringify(map, null, 2));
  return map;
}

// ---------------------------------------------------------------------------
// API Surface Generator
// ---------------------------------------------------------------------------

export async function generateApiSurface(projectRoot: string): Promise<ApiSurface> {
  const contextDir = join(projectRoot, "swarm/context");
  await mkdir(contextDir, { recursive: true });

  // Read main.py to find route registrations
  const mainPath = join(projectRoot, "backend/app/main.py");
  let routeModules: ApiSurface["routeModules"] = [];

  try {
    const content = await readFile(mainPath, "utf-8");
    const includeMatches = content.matchAll(/app\.include_router\(\s*(\w+)(?:_router)?/g);

    for (const match of includeMatches) {
      const name = match[1];
      const routeFile = join(projectRoot, `backend/app/routes/${name}.py`);
      try {
        const routeContent = await readFile(routeFile, "utf-8");
        const endpointCount = (routeContent.match(/@router\.(get|post|put|delete|patch|websocket)/g) || []).length;
        routeModules.push({
          name,
          file: `backend/app/routes/${name}.py`,
          endpointCount,
        });
      } catch {
        routeModules.push({ name, file: `backend/app/routes/${name}.py`, endpointCount: 0 });
      }
    }
  } catch {
    // main.py may not exist
  }

  const surface: ApiSurface = {
    generatedAt: new Date().toISOString(),
    totalEndpoints: routeModules.reduce((sum, r) => sum + r.endpointCount, 0),
    routeModules,
  };

  await writeFile(join(contextDir, "api-surface.json"), JSON.stringify(surface, null, 2));
  return surface;
}

// ---------------------------------------------------------------------------
// Context for specific agent
// ---------------------------------------------------------------------------

export async function getContextForAgent(
  agentId: string,
  projectRoot: string
): Promise<{ agent: AgentInfo; relevantFiles: string[]; context: string }> {
  const agent = getAgent(agentId);
  if (!agent) throw new Error(`Agent not found: ${agentId}`);

  const relevantFiles: string[] = [];
  const contextParts: string[] = [];

  contextParts.push(`# Context for ${agent.name}`);
  contextParts.push(`Division: ${agent.division}`);
  contextParts.push(`Description: ${agent.description}`);
  contextParts.push(`Scope: ${agent.scope.join(", ")}`);
  contextParts.push("");

  // Load relevant files
  for (const scopePath of agent.scope) {
    const fullPath = join(projectRoot, scopePath);
    try {
      const content = await readFile(fullPath, "utf-8");
      relevantFiles.push(scopePath);
      contextParts.push(`## ${scopePath}`);
      // Truncate large files to first 100 lines
      const lines = content.split("\n");
      if (lines.length > 100) {
        contextParts.push(lines.slice(0, 100).join("\n"));
        contextParts.push(`\n... (${lines.length - 100} more lines)`);
      } else {
        contextParts.push(content);
      }
      contextParts.push("");
    } catch {
      // File or directory, skip
    }
  }

  return {
    agent,
    relevantFiles,
    context: contextParts.join("\n"),
  };
}
