[kubernetes_cluster]
{% for ip in ips %}
node{{ loop.index }} ansible_host={{ ip }} ansible_user=ubuntu
{% endfor %}