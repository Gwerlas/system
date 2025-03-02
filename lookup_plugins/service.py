#!/usr/bin/python
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r"""
  name: service
  author: Yoann Gauthier-Colin <yoann@gwerlas.net>
  version_added: "0.15"
  short_description: get the accurate service name
  description:
      - This lookup returns the service name for the remote system.
  options:
    _terms:
      description: service name to search
      required: True
"""
import re
from ansible.errors import AnsibleError, AnsibleUndefinedVariable
from ansible.plugins.loader import lookup_loader
from ansible.plugins.lookup import LookupBase
from ansible.utils.display import Display

display = Display()

class LookupModule(LookupBase):

    def get_var(self, var_name):
        lookup = lookup_loader.get(
            'ansible.builtin.vars',
            loader=self._loader,
            templar=self._templar
        )

        return lookup.run([var_name])[0]
    
    def get_services(self):
        try:
            services_map = self.get_var('services_map')
        except AnsibleUndefinedVariable:
            services_map = {}

        display.v("Services map: %s" % services_map)
        return services_map

    def run(self, terms, variables=None, **kwargs):
        if variables is not None:
            self._templar.available_variables = variables

        # Get the current service manager (eg. systemd)
        svc_mgr = self.get_var('ansible_service_mgr')

        services_map = self.get_services()

        ret = []

        for term in terms:
            display.vv("Term: %s" % term)

            if term in services_map:
                value = services_map[term]
            else:
                value = term
            
            ret.append(value + '.service' if svc_mgr == 'systemd' else value)
                
        return ret
