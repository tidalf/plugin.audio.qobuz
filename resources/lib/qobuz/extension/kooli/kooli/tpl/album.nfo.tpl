
<album>
  <title>{{title}}</title>
  {% for genre in genres_list %}
  <genre>{{genre}}</genre>
  {% endfor %}
  <releasedate>{{released_at}}</releasedate>
  <type>{{type}}</type>
  <thumb>{{image.small}}</thumb>
</album>
