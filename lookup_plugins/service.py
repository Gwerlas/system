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

from ansible.plugins.lookup import LookupBase
from ansible.utils.display import Display

display = Display()

class LookupModule(LookupBase):
    def run(self, terms, variables=None, **kwargs):
        if variables is None:
            variables = {}

        svc_mgr = variables.get('ansible_facts').get('service_mgr', 'systemd')
        services_map = variables.get('services_map', {})

        display.v(f"Service manager: {svc_mgr}, Services map: {services_map}")

        ret = []
        for term in terms:
            value = services_map.get(term, term)
            ret.append(f"{value}.service" if svc_mgr == 'systemd' else value)

        return ret
