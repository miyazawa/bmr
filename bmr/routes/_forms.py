from wtforms import Form, BooleanField, StringField, PasswordField, validators

class SearchForm(Form):
    search = StringField('Search', [validators.Length(min=4, max=25)])

def search_form(form):
    return SearchForm(form)
