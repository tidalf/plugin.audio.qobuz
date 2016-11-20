<h3>Favorites</h3>
{% if albums is defined %}
<li>
<h4>Albums</h4>
{% for album in albums['items'] %}
  <ul>
    <a href="/qobuz/favorite/albums/{{album.id}}">{{album.title}} - {{ album.title }}</a>
  </ul>
{% endfor %}
</li>
{% endif %}
{% if tracks is defined %}
<li>
<h4>Tracks</h4>
{% for track in tracks['items'] %}
  <ul>
    <a href="/qobuz/favorite/tracks/{{track.id}}">{{track.artist}} - {{ track.title }}</a>
  </ul>
{% endfor %}
</li>
{% endif %}
{% if artists is defined %}
<li>
<h4>Artists</h4>
{% for artist in artists['items'] %}
  <ul>
    <a href="/qobuz/favorite/artists/{{artist.id}}">{{artist.name}} ({{ artis.genre }})</a>
  </ul>
{% endfor %}
</li>
{% endif %}
