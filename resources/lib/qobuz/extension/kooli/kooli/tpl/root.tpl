{% for child in childs %}
  <a href="http://127.0.0.1:33574/qobuz/root/{{child.label}}">
    {{child.label}}
  </a>
{% endfor %}
