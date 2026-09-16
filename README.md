# 🛠️ Discord Setup Bot

Bot que configura automáticamente un servidor de Discord: crea roles, categorías, canales y un mensaje de bienvenida con botones para elegir roles.

## 🚀 Puesta en marcha (local)

1. Creá un bot en [discord.com/developers](https://discord.com/developers/applications)
2. Activá **SERVER MEMBERS INTENT** y **MESSAGE CONTENT INTENT** en la página del bot
3. Copiá el token a `config.json`
4. Instalá dependencias: `pip install -r requirements.txt`
5. Ejecutá: `python main.py`

Para invitarlo a tu servidor con permisos de administrador:
```
https://discord.com/oauth2/authorize?client_id=TU_ID_BOT&permissions=8&scope=bot%20applications.commands
```

## ☁️ Hosteo con Railway

El proyecto ya tiene `Procfile`, `railway.json` y `.gitignore`. El token se lee de la variable de entorno `DISCORD_TOKEN` (y como respaldo desde `config.json`).

### Manual (sin Git)

1. Entrá a [railway.app](https://railway.app) y logueate
2. **New Project** → **Deploy from template** → elegí **"Blank"**
3. En **Settings → Source**, vas a necesitar subir el código. La forma más directa:
   - Creá un repo en GitHub y pusheá esta carpeta, **o**
   - Usá **Deploy from repo** conectando tu cuenta de GitHub
4. En **Variables**, agregá:
   - `DISCORD_TOKEN` = tu token del bot
   - `DISCORD_TOKEN` es la única obligatoria
5. Railway detecta `Procfile`/`railway.json` solo:
   - **Build**: Nixpacks (detecta Python automáticamente)
   - **Start**: `python main.py`
6. **Deploy**. Cuando el log muestre `✅ Bot conectado como ...`, vas a tu servidor y escribís `/setup`

### Checklist para que funcione YA

| Requisito | Dónde |
|---|---|
| Token del bot | Developer Portal → Applications → tu bot → Bot → Token |
| Intents activados | mismo menú, sección **Privileged Gateway Intents** |
| Bot invitado al server | URL de invitación arriba (permissions=8 = admin) |
| Variable `DISCORD_TOKEN` en Railway | Deploy → Variables |
| Bot en línea en Railway | Deploy → Deployments → log sin errores |

> ⚠️ **Secreto**: el token en Railway debe ir en **Variables**, NUNCA commitearlo en `config.json` (por eso está en `.gitignore`).

## Uso

| Comando | Descripción |
|---------|-------------|
| `/setup` | Crea/actualiza roles, categorías, canales y mensaje de bienvenida (solo el dueño) |
| `/roles` | Muestra el panel interactivo de roles |
| `!setup` | Igual que `/setup` pero por texto (dueño/administradores) |
| `!roles` | Igual que `/roles` pero por texto |

## Estructura que crea

**Roles:** 👑 Fabri, 🛡️ Admin, 🛡️ Mod, 🎮 Gamer, 👥 Seguidor

**Categorías y canales:**
- 📋 INFORMACIÓN → 📜-reglas, 📢-anuncios
- 📢 COMUNICACIÓN → 💬-general, 🔊-general-voz
- 🎬 CONTENIDO → 🎮-clips, 🔴-streams, 🎥-vods, 📀-videos
- 🖼️ MEDIA → ✨-multimedia, 😂-memes

Y además deja el mensaje de bienvenida con botones de roles en #💬-general.

> 💡 El comando `/setup` es **idempotente**: si un rol o canal ya existe no lo duplica, así podés correrlo todas las veces que quieras.