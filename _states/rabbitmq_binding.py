# -*- coding: utf-8 -*-
"""
Manage RabbitMQ Binding
=============================

Example:

.. code-block:: yaml

    my-new-binding:
      rabbitmq_binding.present:
        - name: my-new-binding
        - destination: my-new-queue
        - destination_type: queue
        - routing_key: routingkey
        - user: guest
        - passwd: guest
        - port: 15672
        - vhost: '/'
"""

# Import python libs
from __future__ import absolute_import
import logging

# Import salt libs
import salt.utils

log = logging.getLogger(__name__)


def __virtual__():
    """
    Only load if RabbitMQ is installed.
    """
    return salt.utils.which('rabbitmqadmin') is not None


def present(name,
            destination,
            destination_type,
            routing_key='',
            user='guest',
            passwd='guest',
            port=15672,
            vhost='/',
            arguments=()):
    """
    Ensure the RabbitMQ Binding exists.

    name
        Binding name

    destination
        Initial destination of e.g. queue name

    destination_type
        Initial type of destination e.g. "queue"

    routing_key
        Initial value for routing key
        Default to ''

    user
        Initial user permission to set on the Binding, if present

    passwd
        Password for user permission to set on the Binding, if present

    port
        Initial target port for localhost
        Defaults to 15672

    vhost
        Initial vhost to which the binding is linked to
        Defaults to '/'

    arguments
        A list of argument keys

    """
    ret = {'name': name, 'result': True, 'comment': '', 'changes': {}}

    binding_exists = __salt__['rabbitmq_extended.binding_exists'](name, destination, destination_type,
                                                                  routing_key, 'localhost',
                                                                  port, user, passwd, vhost)

    if binding_exists:
        ret['comment'] = 'Binding \'{0}\' for vhost \'{1}\' already exists.'.format(name, vhost)
        return ret

    if not __opts__['test']:
        result = __salt__['rabbitmq_extended.add_binding'](name, destination, destination_type, routing_key,
                                                           'localhost', port, user, passwd, vhost, arguments)
        if 'Error' in result:
            ret['result'] = False
            ret['comment'] = result['Error']
            return ret
        elif 'Added' in result:
            ret['comment'] = result['Added']

    # If we've reached this far before returning, we have changes.
    ret['changes'] = {'old': '', 'new': name}

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = 'Binding \'{0}\' for vhost \'{1}\' will be created.'.format(name, vhost)

    return ret


def absent(name,
           destination, routing_key, destination_type,
           user='guest', passwd='guest', port=15672, vhost='/'):
    """
    Ensure the RabbitMQ Binding is absent

    name
        Name of the Binding to remove

    destination
        Initial destination of e.g. queue name

    destination_type
        Initial type of destination e.g. "queue"

    routing_key
        Initial value for routing key

    user
        Initial user permission to set on the Binding, if present

    passwd
        Password for user permission to set on the Binding, if present

    port
        Initial target port for localhost
        Defaults to 15672

    vhost
        Initial vhost to which the Binding is linked to
        Defaults to '/'

    """
    ret = {'name': name, 'result': True, 'comment': '', 'changes': {}}

    properties_key = __salt__['rabbitmq_extended.binding_exists_with_props'](name, destination, destination_type, routing_key,
                                                                             'localhost', port, user, passwd, vhost)

    if not properties_key:
        ret['comment'] = 'Binding \'{0}\' for vhost \'{1}\' not exists.'.format(name, vhost)
        return ret

    if not __opts__['test']:
        result = __salt__['rabbitmq_extended.delete_binding'](name, destination, destination_type, properties_key,
                                                              'localhost', port, user, passwd, vhost)
        if 'Error' in result:
            ret['result'] = False
            ret['comment'] = result['Error']
            return ret
        elif 'Deleted' in result:
            ret['comment'] = result['Deleted']

    # If we've reached this far before returning, we have changes.
    ret['changes'] = {'new': '', 'old': name}

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = 'Exchange \'{0}\' will be removed from vhost \'{1}\'.'.format(name, vhost)

    return ret
