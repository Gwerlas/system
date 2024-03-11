#!/usr/bin/python

# Inspired from the comment of pawamoy :
# https://github.com/copier-org/copier/issues/208#issuecomment-795702871

import re
import unicodedata

class FilterModule(object):
    def filters(self):
        return {
            'slugify': self.slugify
        }

    def slugify(self, value, remove_variables=False):
        """
        Remove $variables if remove_variables is True.
        Convert to ASCII.
        Convert spaces or repeated dashes to single dashes.
        Remove characters that aren't alphanumerics, underscores, or hyphens.
        Convert to lowercase.
        Also strip leading and trailing whitespace, dashes, and underscores.
        """
        value = str(value)
        if remove_variables:
            value = re.sub(r'\$[\w]+', '', value)
        value = unicodedata.normalize('NFKC', value).encode('ascii', 'ignore').decode('ascii')
        value = re.sub(r'[^\w\s-]', '', value.lower())
        return re.sub(r'[-\s]+', '-', value).strip('-_')
