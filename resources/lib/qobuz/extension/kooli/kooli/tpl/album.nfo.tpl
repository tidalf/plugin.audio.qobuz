
<album>
  <title>{{title}}</title>
  <artist>{{artist.name}}</artist>
  {% for genre in genres_list %}
  <genre>{{genre}}</genre>
  {% endfor %}
  <releasedate>{{released_at}}</releasedate>
  <type>{{type}}</type>
  <thumb>{{image.small}}</thumb>
  <label>{{label.name}}</label>
  {% for track in tracks['items'] %}
    <track>
      <position>{{track.media_number}}</position>
      <title>{{track.title}}</title>
      <duration>{{track.duration}}</duration>
    </track>
  {% endfor %}
<review>{%- if true -%}
{{catchline}}
{{description}}
Duration : {{duration / 60}}mn
Tracks   : {{tracks_count}}
Media    : {{media_count}}
HiRes    : {{hires}}
Sales factors (monthly/yearly): {{product_sales_factors_monthly}} / {{product_sales_factors_yearly}}
Copyright: {{copyright}}
{% endif %}</review>
</album>
