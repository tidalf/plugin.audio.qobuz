<html>
<head>
  <title>{{title}}</title>
</head>
<body>
{% for track in tracks['items'] %}
  <a href="/qobuz/{{id}}/{{track.id}}.mpc">
    {{track.track_number}}. {{title}} / {{track.name}}
  </a>
{% endfor %}
</body>
</html>
