# saltstack_rabbitmq_extended
Missing Saltstack state modules for RabbitMQ

This project extends saltstack state modules to configure the exchanges, queues and bindings in RabbitMQ

Just copy the 2 folders _states and _modules into your file_roots as documented here:
https://docs.saltstack.com/en/latest/ref/states/writing.html#states-are-easy-to-write

How to use the states?

# Manage Exchanges
# Creates the exchange "my-new-exchange"
add_my-new-exchange:
  rabbitmq_exchange.present:
   - name: my-new-exchange
   - user: user
   - passwd: 'password'
   - type: fanout
   - durable: True
   - internal: False
   - auto_delete: False
   - vhost: test_vhost
   - arguments:
     - 'alternate-**exchange': 'amq.fanout'
     - 'test-header': 'testing'

# Removes the exchange "my-test-exchange"
remove_my-new-exchange:
  rabbitmq_exchange.absent:
    - name: my-new-exchange
    - vhost: test_vhost   
    - user: user
    - passwd: 'password'

# Manage Queues
# Creates the queue "my-new-queue"
add_my-new-queue:
  rabbitmq_queue.present:
    - name: my-new-queue
    - user: user
    - passwd: 'password'
    - durable: True
    - auto_delete: False
    - vhost: test_vhost
    - arguments:
      - 'x-message-ttl': 8640000
      - 'x-expires': 8640000
      - 'x-dead-letter-exchange': 'my-new-exchange'

# Removes the queue "my-new-queue"
remove_my-new-queue:
  rabbitmq_queue.absent:
    - name: my-new-queue
    - vhost: test_vhost
    - user: user
    - passwd: 'password'
    
# Manage Bindings
# Creates the Binding "my-new-binding"
add_my-new-binding:
  rabbitmq_binding.present:
    - name: my-new-binding
    - destination_type: queue
    - destination: my-new-queue
    - routing_key: a_routing_key_string
    - user: user
    - passwd: 'password'
    - vhost: test_vhost
    - arguments:
      - 'x-message-ttl': 8640000

# Removes the binding "my-new-binding"
remove_my-new-binding:
  rabbitmq_binding.absent:
    - name: my-new-binding
    - destination_type: queue
    - destination: my-new-queue
    - routing_key: a_routing_key_string
    - vhost: test_vhost
    - user: user
    - passwd: 'password'
