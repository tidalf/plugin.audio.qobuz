<h3>Favorites</h3>
{% if albums is defined %}
{% for album in albums['items'] %}
<a href="/qobuz/favorite/albums/{{album.id}}">{{ album.artist }} - {{ album.title }}</a><br />
{% endfor %}
{% endif %}
{% if tracks is defined %}
{% for track in tracks['items'] %}
<a href="/qobuz/favorite/tracks/{{track.id}}">{{track.artist}} - {{ track.title }}</a><br />
{% endfor %}
{% endif %}
{% if artists is defined %}
{% for artist in artists['items'] %}
<a href="/qobuz/favorite/artists/{{artist.id}}">{{artist.name}} ({{ artis.genre }})</a><br />
{% endfor %}
{% endif %}
