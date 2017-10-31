# -*- coding: utf-8 -*-
"""
Manage RabbitMQ Queue
=============================

Example:

.. code-block:: yaml

    my-new-queue:
      rabbitmq_queue.present:
        - name: my-new-queue
        - user: guest
        - passwd: guest
        - durable: True
        - auto_delete: False
        - port: 15672
        - vhost: '/'
        - arguments:
          - "x-message-ttl": 86400000
          - "x-expires":86400000
          - "x-dead-letter-exchange":"deadletters.fanout"
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
            user='guest',
            passwd='guest',
            durable=False,
            auto_delete=False,
            port=15672,
            vhost='/',
            arguments=()):
    """
    Ensure the RabbitMQ Queue exists.

    name
        Queue name

    user
        Initial user permission to set on the Queue, if present
        Defaults to guest

    passwd
        Password for user permission to set on the Queue, if present
        Defaults to guest

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
        Initial vhost to which the Queue is linked to
        Defaults to '/'

    arguments
        A list of argument value: keys
        - x-message-ttl: number
        - x-expires: number
        - x-max-length: number
        - x-max-length-bytes: number
        - x-dead-letter-exchange: string
        - x-dead-letter-routing-key: string
        - x-max-priority: number

    """
    ret = {'name': name, 'result': True, 'comment': '', 'changes': {}}

    queue_exists = __salt__['rabbitmq_extended.queue_exists'](name, 'localhost', port, user, passwd, vhost)

    if queue_exists:
        ret['comment'] = 'Queue \'{0}\' for vhost \'{1}\' already exists.'.format(name, vhost)
        return ret

    if not __opts__['test']:
        result = __salt__['rabbitmq_extended.add_queue'](name, 'localhost', port, user, passwd, vhost, durable,
                                                         auto_delete, arguments)
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
        ret['comment'] = 'Queue \'{0}\' for vhost \'{1}\' will be created.'.format(name, vhost)

    return ret


def absent(name,
           user='guest',
           passwd='guest',
           port=15672,
           vhost='/'):
    """
    Ensure the RabbitMQ Queue is absent

    name
        Name of the Queue to remove

    user
        Initial user permission to set on the Queue, if present

    passwd
        Password for user permission to set on the Queue, if present

    port
        Initial target port for localhost
        Defaults to 15672

    vhost
        Initial vhost to which the Queue is linked to
        Defaults to '/'

    """
    ret = {'name': name, 'result': True, 'comment': '', 'changes': {}}

    queue_exists = __salt__['rabbitmq_extended.queue_exists'](name, 'localhost', port, user, passwd, vhost)

    if not queue_exists:
        ret['comment'] = 'Queue \'{0}\' for vhost \'{1}\' already not exists.'.format(name, vhost)
        return ret

    if not __opts__['test']:
        result = __salt__['rabbitmq_extended.delete_queue'](name, 'localhost', port, user, passwd, vhost)
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
        ret['comment'] = 'Queue \'{0}\' will be removed from vhost \'{1}\'.'.format(name, vhost)

    return ret
