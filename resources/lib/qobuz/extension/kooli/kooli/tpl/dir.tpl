<html>
<head>
  <title>{{title}}</title>
</head>
<body>
{% for track in tracks['items'] %}
  <a href="/qobuz/{{id}}/{{track.id}}/file.mpc">
    {{track.track_number}}. {{title}} / {{track.name}}
  </a>
{% endfor %}
</body>
</html>
