# -*- coding: utf-8 -*-
"""
Extended Module to provide RabbitMQ compatibility to Salt.
Todo: A lot, need to add cluster support, logging, and minion configuration
data.
"""
from __future__ import absolute_import

# Import python libs
import json
import logging

# Import salt libs
import salt.utils
import salt.utils.itertools
import salt.ext.six as six
from salt.exceptions import SaltInvocationError
from salt.ext.six.moves import range
from salt.exceptions import CommandExecutionError

log = logging.getLogger(__name__)


def __virtual__():
    """
    Verify RabbitMQ is installed.
    """
    rabbitmqctl = salt.utils.which('rabbitmqctl') is not None
    rabbitmqadmin = salt.utils.which('rabbitmqadmin') is not None
    return rabbitmqctl and rabbitmqadmin


def _format_response(response, msg):
    error = 'RabbitMQ command failed: {0}'.format(response)
    if isinstance(response, dict):
        if response['retcode'] != 0:
            raise CommandExecutionError(error)
        else:
            msg = response['stdout']
    else:
        if 'Error' in response:
            raise CommandExecutionError(error)
    return {
        msg: response
    }


def _safe_output(line):
    """
    Looks for rabbitmqctl warning, or general formatting, strings that aren't
    intended to be parsed as output.
    Returns a boolean whether the line can be parsed as rabbitmqctl output.
    """
    return not any([
        line.startswith('Listing') and line.endswith('...'),
        '...done' in line,
        line.startswith('WARNING:')
    ])


def _strip_listing_to_done(output_list):
    """
    Conditionally remove non-relevant first and last line,
    "Listing ..." - "...done".
    outputlist: rabbitmq command output split by newline
    return value: list, conditionally modified, may be empty.
    """
    return [line for line in output_list if _safe_output(line)]


def _output_to_dict(cmdoutput, values_mapper=None):
    """
    Convert rabbitmqctl output to a dict of data
    cmdoutput: string output of rabbitmqctl commands
    values_mapper: function object to process the values part of each line
    """
    ret = {}
    if values_mapper is None:
        values_mapper = lambda string: string.split('\t')

    # remove first and last line: Listing ... - ...done
    data_rows = _strip_listing_to_done(cmdoutput.splitlines())

    for row in data_rows:
        try:
            key, values = row.split('\t', 1)
        except ValueError:
            # If we have reached this far, we've hit an edge case where the row
            # only has one item: the key. The key doesn't have any values, so we
            # set it to an empty string to preserve rabbitmq reporting behavior.
            # e.g. A user's permission string for '/' is set to ['', '', ''],
            # Rabbitmq reports this only as '/' from the rabbitmqctl command.
            log.debug('Could not find any values for key \'{0}\'. '
                      'Setting to \'{0}\' to an empty string.'.format(row))
            ret[row] = ''
            continue
        ret[key] = values_mapper(values)
    return ret


def exchange_exists(name, host='localhost',port=15672,
                    user='guest', passwd='guest', vhost='/', runas=None):
    """
    Return whether the exchange exists based on rabbitmqadmin list exchanges.

    CLI Example:

    .. code-block:: bash

        salt '*' rabbitmq_extended.rabbit_exchange rabbit_host rabbit_port rabbit_user rabbit_password rabbit_vhost
    """
    if runas is None:
        runas = salt.utils.get_user()
    res = __salt__['cmd.run'](
        ['rabbitmqadmin', 'list', 'exchanges', '-H', host, '-P', port,
         '-u', user, '-p', passwd, '-V', vhost, '--format=raw_json'],
        python_shell=False, runas=runas)
    for item in json.loads(res):
        if item['name'] == name:
            return True
    return False


def queue_exists(name, host='localhost',port=15672,
                 user='guest', passwd='guest', vhost='/', runas=None):
    """
    Return whether the exchange exists based on rabbitmqadmin list queues.

    CLI Example:

    .. code-block:: bash

        salt '*' rabbitmq_extended.queue_exists rabbit_host rabbit_port rabbit_user rabbit_password rabbit_vhost
    """
    if runas is None:
        runas = salt.utils.get_user()
    res = __salt__['cmd.run'](
        ['rabbitmqadmin', 'list', 'queues', '-H', host, '-P', port,
         '-u', user, '-p', passwd, '-V', vhost, '--format=raw_json'],
        python_shell=False, runas=runas)
    for item in json.loads(res):
        if item['name'] == name:
            return True
    return False


def binding_exists(name, destination, destination_type, routing_key, host='localhost',port=15672,
                   user='guest', passwd='guest', vhost='/', runas=None):
    """
    Return whether the binding exists based on rabbitmqadmin list bindings.

    CLI Example:

    .. code-block:: bash

        salt '*' rabbitmq_extended.binding_exists rabbit_destination rabbit_destination_type rabbit_routing_key
                 abbit_host rabbit_port rabbit_user rabbit_password rabbit_vhost
    """
    if runas is None:
        runas = salt.utils.get_user()
    res = __salt__['cmd.run'](
        ['rabbitmqadmin', 'list', 'bindings', '-H', host, '-P', port,
         '-u', user, '-p', passwd, '-V', vhost, '--format=raw_json'],
        python_shell=False, runas=runas)
    for item in json.loads(res):
        if item['source'] == name and item['destination'] == destination \
                and item['destination_type'] == destination_type \
                and item['routing_key'] == routing_key \
                and item['vhost'] == vhost:
            return True
    return False


def binding_exists_with_props(name, destination, destination_type, routing_key, host='localhost',port=15672,
                              user='guest', passwd='guest', vhost='/', runas=None):
    """
    Return whether the binding exists based on rabbitmqadmin list bindings returns with properties_key.

    CLI Example:

    .. code-block:: bash

        salt '*' rabbitmq_extended.binding_exists_with_props rabbit_destination rabbit_destination_type rabbit_routing_key
                 abbit_host rabbit_port rabbit_user rabbit_password rabbit_vhost
    """
    if runas is None:
        runas = salt.utils.get_user()
    res = __salt__['cmd.run'](
        ['rabbitmqadmin', 'list', 'bindings', '-H', host, '-P', port,
         '-u', user, '-p', passwd, '-V', vhost, '--format=raw_json'],
        python_shell=False, runas=runas)
    for item in json.loads(res):
        if item['source'] == name and item['destination'] == destination \
                and item['destination_type'] == destination_type \
                and item['routing_key'] == routing_key \
                and item['vhost'] == vhost:
            return item['properties_key']
    return None


def add_exchange(exchange, host='localhost', port=15672, user='guest', passwd='guest', vhost='/',
                 type='fanout', durable=False, internal=False, auto_delete=False, arguments=(), runas=None):
    """
    Adds an exchange via rabbitmqadmin add_exchange.

    CLI Example:

    .. code-block:: bash

        salt '*' rabbitmq_extended.add_exchange '<exchange_name>' '<host>' '<port>' '<user>' '<passwd>'
                '<vhost_name>' '<type>' '<durable>' '<internal>' '<auto_delete>' '<arguments>'
    """
    if runas is None:
        runas = salt.utils.get_user()
    args = {}
    for item in arguments:
        args.update(item)
    res = __salt__['cmd.run'](
        ['rabbitmqadmin', 'declare', 'exchange', '-H', host, '-P', port, '-u', user, '-p', passwd, '-V', vhost,
         'name={0}'.format(exchange), 'type={0}'.format(type), 'durable=%s' % str(durable).lower(),
         'internal=%s' % str(internal).lower() ,
         'auto_delete=%s' % str(auto_delete).lower(),
         'arguments=%s' % json.dumps(args)],
        runas=runas,
        python_shell=False)
    msg = 'Added'
    return _format_response(res, msg)


def add_queue(queue, host='localhost', port=15672, user='guest', passwd='guest',
              vhost='/', durable=False, auto_delete=False, arguments=(), runas=None):
    """
    Adds a queue via rabbitmqadmin add_queue.

    CLI Example:

    .. code-block:: bash

        salt '*' rabbitmq_extended.add_queue '<queue_name>' '<host>' '<port>' '<user>' '<passwd>'
                '<vhost_name>' '<durable>' '<auto_delete>' '<arguments>'
    """
    if runas is None:
        runas = salt.utils.get_user()
    args = {}
    for item in arguments:
        args.update(item)
    res = __salt__['cmd.run'](
        ['rabbitmqadmin', 'declare', 'queue', '-H', host, '-P', port, '-u', user, '-p', passwd, '-V', vhost,
         'name={0}'.format(queue), 'durable=%s' % str(durable).lower(),
         'auto_delete=%s' % str(auto_delete).lower(),
         'arguments=%s' % json.dumps(args)],
        runas=runas,
        python_shell=False)
    msg = 'Added'
    return _format_response(res, msg)


def add_binding(binding, destination, destination_type, routing_key,
                host='localhost', port=15672, user='guest', passwd='guest',
                vhost='/', arguments=(), runas=None):
    """
    Adds a binding via rabbitmqadmin add_binding.

    CLI Example:

    .. code-block:: bash

        salt '*' rabbitmq_extended.add_binding '<binding_name>' '<host>' '<port>' '<user>' '<passwd>'
                '<vhost_name>' '<durable>' '<auto_delete>' '<arguments>'
    """
    if runas is None:
        runas = salt.utils.get_user()
    args = {}
    for item in arguments:
        args.update(item)
    res = __salt__['cmd.run'](
        ['rabbitmqadmin', 'declare', 'binding', '-H', host, '-P', port, '-u', user, '-p', passwd, '-V', vhost,
         'source={0}'.format(binding),
         'destination_type={0}'.format(destination_type),
         'destination={0}'.format(destination),
         'routing_key={0}'.format(routing_key),
         'arguments=%s' % json.dumps(args)],
        runas=runas,
        python_shell=False)
    msg = 'Added'
    return _format_response(res, msg)


def delete_exchange(exchange, host='localhost', port=15672, user='guest', passwd='guest', vhost='/', runas=None):
    """
    Deletes an exchange rabbitmqadmin delete_exchange.

    CLI Example:

    .. code-block:: bash

        salt '*' rabbitmq_extended.delete_exchange '<exchange_name>' '<host>' '<port>' '<user>' '<passwd>' '<vhost_name>'
    """
    if runas is None:
        runas = salt.utils.get_user()
    res = __salt__['cmd.run'](
        ['rabbitmqadmin', 'delete', 'exchange', 'name={0}'.format(exchange), '-H', host, '-P', port,
         '-u', user, '-p', passwd, '-V', vhost, '--format=table'],
        runas=runas,
        python_shell=False)
    msg = 'Deleted'
    return _format_response(res, msg)


def delete_queue(queue, host='localhost', port=15672, user='guest', passwd='guest', vhost='/', runas=None):
    """
    Deletes a queue rabbitmqadmin delete_queue.

    CLI Example:

    .. code-block:: bash

        salt '*' rabbitmq_extended.delete_queue '<queue_name>' '<host>' '<port>' '<user>' '<passwd>' '<vhost_name>'
    """
    if runas is None:
        runas = salt.utils.get_user()
    res = __salt__['cmd.run'](
        ['rabbitmqadmin', 'delete', 'queue', 'name={0}'.format(queue), '-H', host, '-P', port,
         '-u', user, '-p', passwd, '-V', vhost, '--format=table'],
        runas=runas,
        python_shell=False)
    msg = 'Deleted'
    return _format_response(res, msg)


def delete_binding(binding, destination, destination_type, properties_key,
                   host='localhost', port=15672, user='guest', passwd='guest',
                   vhost='/', runas=None):
    """
    Deletes a binding rabbitmqadmin delete_binding.

    CLI Example:

    .. code-block:: bash

        salt '*' rabbitmq_extended.delete_binding '<binding_name>' '<destination>' '<destination_type>'
                                                  '<properties_key>' '<host>' '<port>'
                                                  '<user>' '<passwd>' '<vhost_name>'
    """
    if runas is None:
        runas = salt.utils.get_user()
    res = __salt__['cmd.run'](
        ['rabbitmqadmin', 'delete', 'binding',
         'source={0}'.format(binding), 'destination={0}'.format(destination),
         'destination_type={0}'.format(destination_type),
         'properties_key={0}'.format(properties_key),
         '-H', host, '-P', port, '-u', user, '-p', passwd, '-V', vhost, '--format=table'],
        runas=runas,
        python_shell=False)
    msg = 'Deleted'
    return _format_response(res, msg)