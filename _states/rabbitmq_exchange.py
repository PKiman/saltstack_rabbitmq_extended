# -*- coding: utf-8 -*-
'''
Manage RabbitMQ Exchange
=============================

Example:

.. code-block:: yaml

    my-new-exchange:
      rabbitmq_exchange.present:
        - name: my-new-exchange
        - user: guest
        - passwd: guest
        - type: fanout
        - durable: True
        - internal: False
        - auto_delete: False
        - port: 15672
        - vhost: '/'
        - arguments:
          - "x-message-ttl": 86400000
          - "x-expires":86400000
'''

# Import python libs
from __future__ import absolute_import
import logging

# Import salt libs
import salt.utils

log = logging.getLogger(__name__)


def __virtual__():
    '''
    Only load if RabbitMQ is installed.
    '''
    return salt.utils.which('rabbitmqadmin') is not None


def present(name,
            user='guest',
            passwd='guest',
            type='fanout',
            durable=False,
            internal=False,
            auto_delete=False,
            port=15672,
            vhost='/',
            arguments=()):
    '''
    Ensure the RabbitMQ Exchange exists.

    name
        Exchange name

    user
        Initial user permission to set on the Exchange, if present
        Defaults to guest

    passwd
        Password for user permission to set on the Exchange, if present
        Defaults to guest

    type
        Initial type of the exchange

    durable
        Initial value durable
        Defaults to False

    internal
        Initial value internal
        Defaults to False

    auto_delete
        Initial value auto_delete
        Defaults to False

    port
        Initial target port for localhost
        Defaults to 15672

    vhost
        Initial vhost to which the exchange is linked to
        Defaults to '/'

    arguments
        A list of argument keys

    '''
    ret = {'name': name, 'result': True, 'comment': '', 'changes': {}}

    exchange_exists = __salt__['rabbitmq_extended.exchange_exists'](name, 'localhost', port, user, passwd, vhost)

    if exchange_exists:
        ret['comment'] = 'Exchange \'{0}\' for vhost \'{1}\' already exists.'.format(name, vhost)
        return ret

    if not __opts__['test']:
        result = __salt__['rabbitmq_extended.add_exchange'](name, 'localhost', port, user, passwd, vhost,
                                                            type, durable, internal, auto_delete, arguments)
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
        ret['comment'] = 'Exchange \'{0}\' for vhost \'{1}\' will be created.'.format(name, vhost)

    return ret


def absent(name,
           user='guest',
           passwd='guest',
           port=15672,
           vhost='/'):
    '''
    Ensure the RabbitMQ Exchange is absent

    name
        Name of the Exchange to remove

    user
        Initial user permission to set on the Exchange, if present

    passwd
        Password for user permission to set on the Exchange, if present

    port
        Initial target port for localhost
        Defaults to 15672

    vhost
        Initial vhost to which the exchange is linked to
        Defaults to '/'

    '''
    ret = {'name': name, 'result': True, 'comment': '', 'changes': {}}

    exchange_exists = __salt__['rabbitmq_extended.exchange_exists'](name, 'localhost', port, user, passwd, vhost)

    if not exchange_exists:
        ret['comment'] = 'Exchange \'{0}\' for vhost \'{1}\' already not exists.'.format(name, vhost)
        return ret

    if not __opts__['test']:
        result = __salt__['rabbitmq_extended.delete_exchange'](name, 'localhost', port, user, passwd, vhost)
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
