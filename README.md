# saltstack_rabbitmq_extended
# The Missing Saltstack state modules for RabbitMQ

This project extends saltstack state modules to configure the exchanges, queues and bindings in RabbitMQ

Just copy the 2 folders _states and _modules into your file_roots as documented here:
https://docs.saltstack.com/en/latest/ref/states/writing.html#states-are-easy-to-write

# Known issues
In case of extending (add additional arguments) existing exchanges, queues and bindings those must be removed and created again.  


How to use the state modules?

```yaml
# Install dependencies
rabbitmq-server.noarch:
  pkg.installed

# make sure rabbitmq is started
rabbitmq-server-service:
  service.running:
    - name: rabbitmq-server
    - enable: True
    - reload: True
    - require:
      - pkg: rabbitmq-server.noarch

# Add a vhost like 
# https://docs.saltstack.com/en/latest/ref/states/all/salt.states.rabbitmq_vhost.html#salt.states.rabbitmq_vhost.present
add_test_vhost:
  rabbitmq_vhost.present:
    - name: test_vhost
    - require:
      - pkg: rabbitmq-server.noarch
      - service: rabbitmq-server-service

# create an administrative user for saltstack
add_user_saltstack:
  rabbitmq_user.present:
    - name: saltstack
    - password: password
    - force: False
    - tags:
      - administrator
    - perms:
      - test_vhost:
        - '.*'
        - '.*'
        - '.*'
    - runas: rabbitmq
    - require:
      - rabbitmq_vhost: add_test_vhost

# Manage Exchanges
# Creates the exchange "my-new-exchange"
add_my-new-exchange:
  rabbitmq_exchange.present:
   - name: my-new-exchange
   - user: saltstack
   - passwd: 'password'
   - type: fanout
   - durable: True
   - internal: False
   - auto_delete: False
   - vhost: test_vhost
   - arguments:
     - 'alternate-**exchange': 'amq.fanout'
     - 'test-header': 'testing'
   - require:
     - rabbitmq_vhost: add_test_vhost
     - rabbitmq_user: add_user_saltstack

# Removes the exchange "my-test-exchange"
remove_my-new-exchange:
  rabbitmq_exchange.absent:
    - name: my-new-exchange
    - vhost: test_vhost   
    - user: saltstack
    - passwd: 'password'

# Manage Queues
# Creates the queue "my-new-queue"
add_my-new-queue:
  rabbitmq_queue.present:
    - name: my-new-queue
    - user: saltstack
    - passwd: 'password'
    - durable: True
    - auto_delete: False
    - vhost: test_vhost
    - arguments:
      - 'x-message-ttl': 8640000
      - 'x-expires': 8640000
      - 'x-dead-letter-exchange': 'my-new-exchange'
    - require:
      - rabbitmq_vhost: add_test_vhost
      - rabbitmq_user: add_user_saltstack
      - rabbitmq_exchange: add_my-new-exchange
      
# Removes the queue "my-new-queue"
remove_my-new-queue:
  rabbitmq_queue.absent:
    - name: my-new-queue
    - vhost: test_vhost
    - user: saltstack
    - passwd: 'password' 
      
# Manage Bindings
# Creates the Binding "my-new-binding"
add_my-new-binding:
  rabbitmq_binding.present:
    - name: my-new-binding
    - destination_type: queue
    - destination: my-new-queue
    - routing_key: a_routing_key_string
    - user: saltstack
    - passwd: 'password'
    - vhost: test_vhost
    - arguments:
      - 'x-message-ttl': 8640000
    - require:
      - rabbitmq_vhost: add_test_vhost
      - rabbitmq_user: add_user_saltstack
      - rabbitmq_queue: add_my-new-queue

# Removes the binding "my-new-binding"
remove_my-new-binding:
  rabbitmq_binding.absent:
    - name: my-new-binding
    - destination_type: queue
    - destination: my-new-queue
    - routing_key: a_routing_key_string
    - vhost: test_vhost
    - user: saltstack
    - passwd: 'password'
    - require:
      - rabbitmq_vhost: add_test_vhost
      - rabbitmq_user: add_user_saltstack    
```
