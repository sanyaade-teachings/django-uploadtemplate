import os

from django.core.files.storage import default_storage
from django.template import TemplateDoesNotExist
from django.template.loaders import filesystem

from uploadtemplate.models import Theme
from uploadtemplate.utils import is_protected_template

class Loader(filesystem.Loader):
    def load_template_source(self, template_name, dirs=None):
        try:
            theme = Theme.objects.get_current()
        except Theme.DoesNotExist:
            raise TemplateDoesNotExist, 'no default theme'

        if is_protected_template(template_name):
            raise TemplateDoesNotExist('Template name is protected')

        # Try the new location first.
        name = os.path.join(theme.theme_files_dir, 'templates', template_name)
        if default_storage.exists(name):
            fp = default_storage.open(name)
            return (fp.read(), name)

        # Then fall back on the old location.
        return super(Loader, self).load_template_source(template_name,
                                                        [theme.template_dir()])

    load_template_source.is_usable = True

_loader = Loader()

def load_template_source(template_name, dirs=None):
    import warnings
    warnings.warn("`uploadtemplate.loader.load_template_source` is deprecated. "
                 "Use `uploadtemplate.loader.Loader` instead.",
                 DeprecationWarning)
    return _loader.load_template_source(template_name, dirs)
load_template_source.is_usable = True
