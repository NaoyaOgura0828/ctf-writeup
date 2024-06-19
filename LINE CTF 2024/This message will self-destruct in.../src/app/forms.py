from wtforms import (
    StringField,
    IntegerField,
    PasswordField,
    FileField,
    validators
)
from wtforms.widgets import (
    HiddenInput
)
from flask_wtf import FlaskForm
from flask_wtf.file import (
    FileAllowed
)

FlaskForm.meta = {'csrf': False}


class AddImageForm(FlaskForm):
    image = FileField(
        'Image', 
        validators=[
            validators.Optional(),
            FileAllowed(['jpg','png'], 'You can upload only Image file (.jpg or .png)')
        ])
    image_url = StringField(
        validators=[
            validators.Optional(),
            validators.URL(message='Please specify valid URL as Image URL'),
            validators.Regexp(r'.+\.(jpg|png)$', message='Image URL must end with ".jpg" or ".png"')
        ]
    )
    password = PasswordField(
        'Password',
        validators=[
            validators.InputRequired('Password is required')
        ]
    )
    id = StringField(
        widget=HiddenInput(),
        validators=[
            validators.Regexp(r'^[0-9a-f]+$'),
            validators.Optional()
        ]
    )

    def validate(self, extra_validators=None):
        if not super(AddImageForm, self).validate(extra_validators):
            return False
        
        if (self.image.data and self.image_url.data) or (not self.image.data and not self.image_url.data):
            self.image.errors.append('Please specify either Image file OR Image URL')
            return False
        
        return True