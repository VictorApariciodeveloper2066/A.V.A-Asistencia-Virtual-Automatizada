# Página de Configuración - AVA

## Funcionalidades Implementadas

### 1. ✅ Datos Personales
- **Editar nombre y apellido**: Los usuarios pueden actualizar su primer nombre y primer apellido
- **Editar email**: Cambiar dirección de correo electrónico
- **Cédula inmutable**: La cédula se muestra pero no puede ser modificada (dato sensible)
- **Endpoint**: `POST /auth/actualizar_perfil`

### 2. ✅ Foto de Perfil
- **Subir avatar**: Los usuarios pueden subir una imagen JPG o PNG
- **Preview en tiempo real**: La imagen se muestra inmediatamente después de subirla
- **Almacenamiento**: Las imágenes se guardan en `/static/uploads/avatars/`
- **Endpoint**: `POST /auth/subir_avatar`

### 3. ✅ Seguridad - Cambiar Contraseña
- **Validación de contraseña actual**: Requiere la contraseña actual para cambiarla
- **Confirmación de nueva contraseña**: Verifica que ambas contraseñas coincidan
- **Encriptación**: Las contraseñas se almacenan con hash seguro
- **Endpoint**: `POST /auth/cambiar_password`

### 4. ✅ Notificaciones por Email
- **Toggle activar/desactivar**: Switch visual para habilitar/deshabilitar notificaciones
- **Notificaciones para estudiantes**: Reciben email cuando se registra su asistencia
- **Notificaciones para profesores**: Pueden recibir resúmenes semanales
- **Campo en BD**: `notificaciones_activas` (Boolean)
- **Endpoint**: `POST /auth/actualizar_notificaciones`

### 5. ✅ Preferencias - Formato de Hora
- **12 horas**: Formato AM/PM (3:45 PM)
- **24 horas**: Formato militar (15:45)
- **Aplicación global**: Afecta la visualización en todo el dashboard
- **Campo en BD**: `formato_hora` (String: '12h' o '24h')
- **Endpoint**: `POST /auth/actualizar_formato_hora`

### 6. ✅ Gestionar Cursos (Solo Estudiantes)
- **Ver cursos inscritos**: Lista de todas las materias actuales
- **Inscribirse en nuevos cursos**: Checkboxes para seleccionar materias
- **Darse de baja**: Deseleccionar cursos para eliminar inscripción
- **Actualización en tiempo real**: Los cambios se reflejan inmediatamente en el dashboard
- **Endpoint**: `POST /auth/gestionar_cursos`

### 7. ✅ Eliminar Cuenta
- **Confirmación doble**: Requiere confirmación y contraseña
- **Eliminación en cascada**: Elimina todas las relaciones del usuario
  - Inscripciones en cursos
  - Registros de asistencia
  - Justificativos
  - Detalles de asistencia
- **Cierre de sesión automático**: Redirige al index después de eliminar
- **Endpoint**: `POST /auth/eliminar_cuenta`

## Campos Agregados al Modelo User

```python
avatar_url = db.Column(db.String(255), nullable=True)
notificaciones_activas = db.Column(db.Boolean, default=True)
formato_hora = db.Column(db.String(10), default='12h')
```

## Rutas Implementadas

| Ruta | Método | Descripción |
|------|--------|-------------|
| `/configuracion` | GET | Página de configuración |
| `/auth/actualizar_perfil` | POST | Actualizar datos personales |
| `/auth/cambiar_password` | POST | Cambiar contraseña |
| `/auth/subir_avatar` | POST | Subir foto de perfil |
| `/auth/actualizar_notificaciones` | POST | Activar/desactivar notificaciones |
| `/auth/actualizar_formato_hora` | POST | Cambiar formato de hora |
| `/auth/gestionar_cursos` | POST | Gestionar inscripciones (estudiantes) |
| `/auth/eliminar_cuenta` | POST | Eliminar cuenta permanentemente |

## Diseño

- **Tema oscuro**: Consistente con el resto de la aplicación
- **Color primario**: #39E079 (verde)
- **Secciones organizadas**: Cada funcionalidad en su propia tarjeta
- **Iconos Material**: Identificación visual clara
- **Responsive**: Funciona en móviles y desktop
- **Zona peligrosa**: Sección especial en rojo para eliminar cuenta

## Seguridad

- ✅ Todas las rutas requieren autenticación (session['username'])
- ✅ Validación de contraseña actual antes de cambiarla
- ✅ Confirmación doble para eliminar cuenta
- ✅ Sanitización de nombres de archivo (secure_filename)
- ✅ Validación de roles (estudiantes vs profesores)

## Instalación

1. Ejecutar el script de actualización de base de datos:
```bash
python actualizar_db_config.py
```

2. Reiniciar la aplicación:
```bash
python app.py
```

3. Acceder a la configuración desde el dashboard haciendo clic en el ícono de configuración en el sidebar

## Notas Técnicas

- Las imágenes de avatar se almacenan con un nombre único: `{user_id}_{timestamp}_{filename}`
- El directorio de avatares se crea automáticamente si no existe
- Los valores por defecto son: notificaciones activas y formato 12h
- La eliminación de cuenta es irreversible y elimina todos los datos relacionados
