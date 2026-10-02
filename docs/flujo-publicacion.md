# Flujo de revisión y publicación

1. Codex prepara el cambio, ejecuta las comprobaciones y presenta el resultado.
2. Luis aprueba el alcance presentado.
3. Codex crea el commit y hace push directo a `origin/main` sin otra confirmación.
4. Una vez conectado el repositorio, Vercel construye y despliega automáticamente desde `main`.

La regla persistente está en `AGENTS.MD`. No hace falta introducir un workflow de GitHub Actions para que Vercel reciba los commits mediante su integración con GitHub.

## Codex remoto sobre esta computadora

`.codex/config.toml` configura `approval_policy = "never"` y `sandbox_mode = "danger-full-access"` para el proyecto de confianza. El acceso completo permite a los comandos acceder también fuera del repositorio. No contiene credenciales y no modifica los valores globales de otros proyectos.

La computadora ya registra este repositorio como trusted en su configuración de usuario. Abrir una sesión nueva para cargar la configuración del proyecto. Si la app impone un perfil distinto, seleccionar Acceso completo en los permisos de esa sesión. Políticas administradas y controles propios de conectores pueden prevalecer sobre estos valores.

El archivo no activa por sí solo el acceso remoto ni conecta dispositivos. Esa conexión se realiza en la app; comprobar que la computadora esté conectada y disponible. Codex Cloud es otro entorno y requiere su propia configuración.

## Pendiente de Vercel

Al disponer de acceso, conectar `Edgarmad/lynx_packaging`, seleccionar `main` como rama de producción y confirmar Astro, Node 24, `npm run build` y salida `dist/`. Revisar el estado efectivo del despliegue. No se ha conectado Vercel en este cambio.

Documentación de permisos: https://learn.chatgpt.com/docs/sandboxing
Referencia de configuración: https://learn.chatgpt.com/docs/config-file/config-reference
