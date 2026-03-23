# 🔒 SISTEMA DE RATE LIMITING - LOGIN

## Resumen

Se ha implementado un sistema de **protección contra fuerza bruta** en el login que bloquea temporalmente la cuenta después de múltiples intentos fallidos.

---

## 🛡️ Cómo funciona

### Escalada de bloqueos:

| Intentos | Estado | Tiempo bloqueo |
|----------|--------|---|
| 1-3 | ⚠️ Advertencia | Sin bloqueo |
| 4 | 🔴 Bloqueado | 10 minutos |
| 5 | 🔴 Bloqueado | 15 minutos |
| 6 | 🔴 Bloqueado | 20 minutos |
| N | 🔴 Bloqueado | (N-3) × 5 minutos |

### Mensajes al usuario:

- **Primer intento fallido:** "Te quedan 3 intentos antes de bloquear la cuenta"
- **Segundo intento fallido:** "Te quedan 2 intentos antes de bloquear la cuenta"
- **Tercer intento fallido:** "Te quedan 1 intentos antes de bloquear la cuenta"
- **Cuarto intento fallido:** "Tu cuenta ha sido bloqueada temporalmente por seguridad. Intenta de nuevo en 10 minutos"
- **Intento durante bloqueo:** "Demasiados intentos fallidos. Intenta de nuevo en X minutos"

---

## 🔧 Implementación técnica

### Archivos modificados:

1. **usuarios/views.py**
   - Funciones auxiliares para rate limiting:
     - `_get_client_ip()` - Obtiene IP del cliente
     - `_get_lock_duration()` - Calcula tiempo de bloqueo
     - `_check_login_lock()` - Verifica si está bloqueado
     - `_increment_login_attempts()` - Traza intentos fallidos
     - `_apply_login_lock()` - Aplica bloqueo temporal
     - `_reset_login_attempts()` - Limpia intentos tras login exitoso
   - Vista `login_view` mejorada con validación de rate limiting

2. **pescaderia_huina/settings.py**
   - Configuración de cache (LocMemCache para rate limiting)
   - Variables en `.env` si es necesario

### Variables de cache utilizadas:

```python
# Rastreo de intentos (se borra después de 30 minutos)
login_attempts:{username}:{ip} = contador

# Bloqueo temporal (expira automáticamente después del tiempo de bloqueo)
login_lock:{username}:{ip} = timestamp_desbloqueo
```

---

## 📍 Comportamiento por IP

El sistema **rastrea intentos por combinación de usuario + IP**:

- Cada IP diferente tiene su propio contador
- Intentos desde la misma IP se acumulan
- Útil para detectar ataques desde múltiples ubicaciones

**Ejemplo:**
```
Usuario: john123
IPX: 3 intentos fallidos (Sin bloqueo)
IPY: 4 intentos fallidos (BLOQUEADO 10 min)
```

---

## ✅ Login exitoso

Al login exitoso:
1. ✅ Se limpia el contador de intentos
2. ✅ Se desbloquea automáticamente el usuario
3. ✅ Usuario puede volver a intentar inmediatamente

---

## 🔑 Recuperación de contraseña

El usuario tiene en **el formulario de login** el link:
```
¿Olvidaste tu contraseña? → {% url 'usuarios:recuperar' %}
```

Flujo de recuperación:
1. Click en "¿Olvidaste tu contraseña?"
2. Ingresar su documento
3. Recibir código por email
4. Cambiar contraseña

---

## 💾 Almacenamiento

- **Cache:** Django LocMemCache (en memoria)
- **Duración:** Intentos persisten 30 minutos, bloqueos expiran automáticamente
- **Ventaja:** No requiere BD extra, no requiere Redis

---

## 🚨 Casos especiales

### ¿Qué pasa si reinicio el servidor?

**El cache se borra**, los intentos se resetean. Esto es por diseño (desarrollo).

En **producción con Redis**, el cache persistiría entre reinicios.

### ¿Qué pasa si cambio de IP?

Cada IP diferente = contador independiente. Útil para:
- ✅ Usuario legítimo usa WiFi diferente
- ✅ Detectar ataque desde múltiples proxies

### ¿El admin puede desbloquear?

Actualmente **no hay panel admin para desbloquear**.Opciones:
1. Esperar a que expire el tiempo
2. Reiniciar el servidor (desarrollo)
3. Redis en producción (más control)

---

## 🔍 Testing del Sistema

Puedes probar el rate limiting en desarrollo:

```bash
# 1. Intenta 3 veces con contraseña incorrecta
# Recibirás advertencias

# 2. En el 4º intento 
# Se bloqueará 10 minutos

# 3. Intenta logearte
# Verás: "Demasiados intentos. Intenta en X minutos"

# 4. Espera 10 minutos o reinicia servidor
# El bloqueo se levanta
```

---

## 📋 Seguridad consideraciones

✅ **Implementado:**
- Rate limiting por IP + usuario
- Escalada de tiempos de bloqueo
- Mensajes claros para usuarios
- Cache automático que expira

⚠️ **Limitaciones actuales:**
- Cache en memoria (no persiste reinicios)
- No hay log de intentos fallidos
- No hay panel admin para desbloquear

🔮 **Mejoras futuras (opcional):**
- Redis para cache persistente
- Logging de intentos en BD
- Panel admin para desbloquear usuarios
- Alertas por email si muchos intentos

---

## ✨ Cambios realizados

**Total líneas agregadas:** ~120 (funciones rate limiting + cache config)
**Riesgo de regresión:** ✅ CERO (funciones aisladas, login view mejorada)
**Funcionalidad existente:** ✅ INTACTA (solo agregado validación de bloqueo)

---

**Implementado:** 23/03/2026
**Estado:** ✅ Completado y testeado
