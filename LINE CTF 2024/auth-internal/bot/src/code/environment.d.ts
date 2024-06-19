export {};

declare global {
    namespace NodeJS {
        interface ProcessEnv {
            DB_PORT: number;
            DB_USER: string;
            ENV:
                | "AUTH_HOST"
                | "EXTERNAL_HOST"
                | "INTERNAL_HOST"
                | "ADMIN_USERNAME"
                | "ADMIN_PASSWORD";
        }
    }
}
