var tw = (function() {
  'use strict';

  var date = new Date();
  var hour = date.getHours();

  return {
    date: date,

    maptime: function() {
      var number = hour;

      $('main > *').each(function() {
        var element = $(this);

        element.attr('data-time', number++);
      });
    },

    coordinates: {
      latitude: false,
      longitude: false
    }
  };
}());

$(function() {
  tw.maptime();
});

$('button[name="coordinates"]').on({
  'click': function() {
    if(navigator.geolocation) {
      var input = $('input[name="origin"]');

      input.prop('disabled', true);

      navigator.geolocation.getCurrentPosition(function(position) {
        input.prop('disabled', false).val('Your Location');

        tw.coordinates.latitude = position.coords.latitude;
        tw.coordinates.longitude = position.coords.longitude;
      });
    } else {
      alert('Geolocation is not supported by this browser.');
    }
  }
});

$('form[name="itinerary"]').on({
  'submit': function(event) {
    var submit = $('button[name="route"]');
    var articles = $('main > article');
    var formData = new FormData(this);
    var sendData = {
      env: 'dev',
      start_location: formData.get('origin'),
      end_location: formData.get('destination'),
      method: formData.get('method')
    };

    if(tw.coordinates.latitude && tw.coordinates.longitude) {
      sendData.start_location = Object.values(tw.coordinates).join();
    }

    if(articles.length) {
      articles.remove();
    }

    submit.prop('disabled', true);

    $.ajax({
      type: 'POST',
      url: 'https://us-central1-travelweather-1548474103293.cloudfunctions.net/travelweather-1',
      data: JSON.stringify(sendData),
      contentType: "application/json; charset=utf-8",
      dataType: 'json',
      crossDomain: true,
      success: function(get) {
        var footer = $('main > footer');
        var template = $('body > template').html();

        $.each(get.hourly, function(index, hour) {
          var cloned = $(template);

          cloned.find('[data-fill]').each(function(index, item) {
            var item = $(item);
            var fill = item.data('fill');

            switch(fill) {
              case 'time':
                item.html(tw.date.toLocaleTimeString('en-US'));
              break;

              case 'timezone':
                // $(item).html(hour.temp);
              break;

              case 'temperature':
                if(hour.temp > 50) {
                  var label = item.prev('dt').find('label');

                  label.prev().prependTo(label.parent());
                }

                item.html(hour.temp);
              break;

              case 'location':
                // $(item).html(hour.temp);
              break;
            }
          });

          cloned.insertBefore(footer);
        });

        tw.maptime();

        submit.text('Reroute').prop('disabled', false);

        $('html, body').animate({
          'scrollTop': $('main > article:first-of-type').offset().top,
        }, 900, 'swing');
      }
    });

    event.preventDefault();
  }
});
