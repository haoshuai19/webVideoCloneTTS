interface ViteEnv {
  VITE_API_URL?: string;
}

interface ImportMeta {
  readonly env: ViteEnv;
}
