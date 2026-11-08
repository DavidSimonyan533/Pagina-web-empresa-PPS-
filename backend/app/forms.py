from flask_wtf import FlaskForm
from wtforms import BooleanField, DateField, PasswordField, SelectField, StringField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, ValidationError

from .content import SERVICES

TAMANOS = [
    ("1-9", "1 a 9 personas"),
    ("10-49", "10 a 49 personas"),
    ("50-249", "50 a 249 personas"),
    ("250+", "250 personas o más"),
]


class RegisterForm(FlaskForm):
    nombre = StringField("Nombre", validators=[DataRequired(), Length(min=2, max=80)])
    email = StringField("Correo electrónico", validators=[DataRequired(), Email(), Length(max=120)])
    empresa = StringField("Empresa (opcional)", validators=[Optional(), Length(max=120)])
    password = PasswordField("Contraseña", validators=[DataRequired(), Length(min=12, max=128, message="Usa entre 12 y 128 caracteres.")])
    confirmar = PasswordField("Repite la contraseña", validators=[DataRequired(), EqualTo("password", message="Las contraseñas no coinciden.")])
    acepto = BooleanField("He leído la política de privacidad", validators=[DataRequired(message="Debes aceptar la política de privacidad.")])

    def validate_password(self, field):
        if self.email.data and field.data.lower() == self.email.data.strip().lower():
            raise ValidationError("La contraseña no puede ser tu correo.")


class LoginForm(FlaskForm):
    email = StringField("Correo electrónico", validators=[DataRequired(), Length(max=120)])
    password = PasswordField("Contraseña", validators=[DataRequired(), Length(max=128)])


class ContactForm(FlaskForm):
    nombre = StringField("Nombre", validators=[DataRequired(), Length(min=2, max=80)])
    email = StringField("Correo electrónico", validators=[DataRequired(), Email(), Length(max=120)])
    asunto = StringField("Asunto", validators=[DataRequired(), Length(min=3, max=120)])
    mensaje = TextAreaField("Mensaje", validators=[DataRequired(), Length(min=10, max=2000)])


class AuditRequestForm(FlaskForm):
    servicio = SelectField("Servicio", choices=[(s["slug"], s["nombre"]) for s in SERVICES], validators=[DataRequired()])
    tamano = SelectField("Tamaño de la organización", choices=TAMANOS, validators=[DataRequired()])
    fecha_preferida = DateField("Fecha preferida de inicio (opcional)", validators=[Optional()])
    descripcion = TextAreaField("Cuéntanos tu situación", validators=[DataRequired(), Length(min=20, max=2000)])
