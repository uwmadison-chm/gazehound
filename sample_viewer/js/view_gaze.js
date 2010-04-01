// A class that handles playing eyetracking data
var gaze_viewer = function(spec) {
  var pub = this;   // public stuff
  var my = {};      // private stuff
  spec = spec || {};
  
  my.point_index = 0;
  my.state = 'paused';
  my.view_data = spec.view_data;
  my.canvas = $(spec.canvas).get(0);
  my.context = my.canvas.getContext('2d');
  my.renderer = eyetrack_renderer({'canvas': my.canvas});
  my.controls_conatiner = $(spec.control_element);
  my.nav_container = $(spec.nav_container);
  my.viewer_groups_element = $(spec.viewer_groups_element);
  my.stim_element = $(spec.stim_element);
  my.stim_img_prefix = spec.stim_img_prefix || '';
  my.thumb_prefix = spec.thumb_prefix || '';
  my.pp_button = $(spec.pp_button);
  my.fps = spec.fps;
  my.time_container = $(spec.time_container);
  my.progress_slider_element = $(spec.progress_slider_element);
  my.elapsed_bar = $(spec.elapsed_bar);
  my.prog_element = my.time_container.children('.first');
  my.len_element = my.time_container.children('.second');
  my.schedule_ms = (1000/my.fps);
  my.playback_speed = 1;
  my.speed_control = $(spec.speed_control);
  my.point_index_offset = 0;
  my.color_scheme = spec.color_scheme;
  
  var toggle_play_pause = function() {
    if (my.state == 'paused') {
      my.state = 'playing';
    } else if (my.state == 'playing') {
      my.state = 'paused';
    }
  }
  
  var play = function(from_start) {
    my.play_started_at = new Date();
    my.rendered_count = 0;
    
    if (from_start || my.point_index >= (my.gaze_len-1)) {
      my.point_index = 0;
      my.point_index_offset = 0;
    }
    my.state = 'playing';
    render_and_schedule();
  };
  pub.play = play;
  var pause = function() {};
  pub.pause = pause;
  
  var set_stim_image = function(stim_name) {
    var pfx = my.stim_img_prefix+'/';
    my.stim_element.attr('src',pfx+my.view_data.stim_images[stim_name]);
  }

  var set_stim_index = function(idx) {
    my.stim_index = idx;
    select_nav_element(my.nav_array[idx]);
    my.stim_name = my.view_data.stims[idx];
    set_stim_image(my.stim_name);
    my.renderer.clear();
    my.stim_data = my.view_data.viewdata[my.stim_name];
    my.point_index = 0;
    my.point_index_offset = 0;
    my.gaze_len = gaze_len();
    update_time_len();
    update_time_progress();
  }
  pub.set_stim_index = set_stim_index;
  
  // Todo, if we need this a lot: memoize!
  var gaze_len = function() {
    var max = 0;
    for (viewer_name in my.stim_data) {
      var view_arrays = my.stim_data[viewer_name];
      for (var i = 0; i < view_arrays.length; i++) {
        if (view_arrays[i].length > max) {
          max = view_arrays[i].length;
        }
      }
    }
    return max;
  }
  pub.gaze_len = gaze_len;
  
  var render_and_schedule = function() {
    var elapsed_ms = (new Date() - my.play_started_at);
    my.rendered_count++;
    var next_index = my.point_index_offset + Math.floor(
      (elapsed_ms*my.playback_speed*my.view_data.samples_per_second) / 
      1000
    );
    if (next_index >= my.gaze_len) {
      next_index = my.gaze_len-1;
      my.state = 'paused';
    }
    if (my.state == 'playing') {
      window.setTimeout(render_and_schedule, my.schedule_ms);
    } else {
      set_play_pause();
      my.point_index_offset = my.point_index;
      console.log(elapsed_ms);
      console.log((my.rendered_count)/(elapsed_ms/1000));
    }
    draw_current_frame();
    my.point_index = next_index;
  }
  
  var progress_percent = function(pct) {
    if (pct) {
      my.point_index = Math.round((pct/100)*(my.gaze_len-1));
    }
    return 100*(my.point_index/(my.gaze_len-1));
  }
  
  var overdraw_all_frames = function() {
    my.renderer.clear();
    for (var i = 0; i < my.gaze_len; i++) {
      my.point_index = i;
      draw_current_points();
    }
  }
  pub.overdraw_all_frames = overdraw_all_frames;
  
  var update_time_len = function() {
    var len_sec = ((my.gaze_len - 1) / my.view_data.samples_per_second);
    my.len_element.text(len_sec.toFixed(3));
  }
  
  var update_time_progress = function() {
    var cur_sec = (my.point_index / my.view_data.samples_per_second);
    my.prog_element.text(cur_sec.toFixed(3));
    var w = progress_percent();
    my.elapsed_bar.width(w.toFixed(2)+'%');
    // Slider ranges from 0-1000, for better resolution...
    my.progress_slider.slider('value', Math.round(w*10));
  }
  
  // Clears the canvas and draws all points on it.
  var draw_current_frame = function() {
    my.renderer.clear();
    draw_current_points();
    update_time_progress();
  }
  pub.draw_current_frame = draw_current_frame;
  
  // Draws a point for each viewing of each subject, for our current
  // point_index.
  var draw_current_points = function() {
    for (viewer_name in my.stim_data) {
      var viewer_data = my.view_data.viewers[
        my.view_data.viewer_directory[viewer_name]];
      var style_data = my.group_styles[viewer_data.group];
      var view_arrays = my.stim_data[viewer_name];
      for (var i = 0; i < view_arrays.length; i++) {
        var p = view_arrays[i][my.point_index];
        if (p) {
          my.renderer.circle(
            {cx:p[0], cy:p[1], r:2}, 
            style_data.fill_style, 
            style_data.stroke_style);
        }
      }
    }
  }
  
  var build_nav = function() {
    // Hold on to these, so we can select an element in set_stim_index()
    my.nav_array = new Array(); 
    my.nav_container.html('');
    for (var i = 0; i < my.view_data.stims.length; i++) {
      var li = nav_li(i);
      my.nav_array[i] = li;
      my.nav_container.append(li);
    }
  }
  
  var select_nav_element = function(elt) {
    elt.siblings('.selected').removeClass('selected');
    elt.addClass('selected');
  }
  
  // Creates a <li> for the navigation, and makes it watch for clicks.
  var nav_li = function(stim_idx) {
    var stim_name = my.view_data.stims[stim_idx]
    var li = new $('<li>').addClass('clearfix');
    var thumb_path = my.thumb_prefix+'/'+my.view_data.stim_images[stim_name];
    li.append($('<img/>').attr('src', thumb_path))
      .append($('<div>').html(my.view_data.stims[stim_idx]))
      .click(function(idx) {
        return function(event) {
          set_stim_index(idx);
        };
      }(stim_idx));
    return li;
  }
  
  var set_play_pause = function() {
    if (my.state == 'playing') {
      my.pp_button.text('Pause');
    } else if (my.state == 'paused'){
      my.pp_button.text('Play');
    }
  }
  
  var set_group_styles = function() {
    my.group_styles = {};
    var groups = my.view_data.viewer_groups;
    for (var i = 0; i < groups.length; i++) {
      var gname = groups[i];
      var scheme = my.color_scheme['group_'+i];
      my.group_styles[gname] = {
        'stroke_style':'rgb('+scheme+')',
        'fill_style':'rgb('+scheme+')',
      };
    }
  }
  
  // Event-handling functions
  var handle_play_pause_click = function(event) {
    toggle_play_pause();
    set_play_pause();
    if (my.state == 'playing') {
      play();
    }
  }
  my.pp_button.click(handle_play_pause_click);
  
  var set_speed_from_control = function(elt) {
    my.playback_speed = parseFloat($(elt).val());
  }
  
  var handle_speed_change = function(event) {
    set_speed_from_control(this);
  }
  my.speed_control.change(handle_speed_change);
  
  var build_progress_slider = function() {
    my.progress_slider = my.progress_slider_element.slider({
      'min': 0,
      'max': 1000,
      'start': function(evt, ui) {
        // Suspend playback
        my.state = "slide-"+my.state;
      },
      'stop': function(evt, ui) {
        // Return playback state to what it was
        my.state = my.state.replace("slide-", "");
        // keep track of where we stopped...
        my.point_index_offset = my.point_index;
        if (my.state == 'playing') {
          play();
        }
      },
      'slide': function(evt, ui) {
        // Wish the slider could have decimal values. Oh well.
        var pct = ui.value/10;
        pct = progress_percent(pct); // Some clipping happens here.
        draw_current_frame();
      }
    });
  }
  
  build_progress_slider();
  build_nav();
  set_stim_index(0);
  set_group_styles();
  
  var debug = function() {
    return my;
  }
  pub.debug = debug;
  
  console.log(debug());
  return pub;
}

var eyetrack_renderer = function(spec) {
  var pub = this;   // public things
  var my = {};      // private things
  spec = spec || {};

  my.canvas = $(spec.canvas).get(0);
  my.context = my.canvas.getContext('2d');
  
  var rectangle = function(shape_data, fill_style, stroke_style, 
                            stroke_width) {
    // Doesn't work yet.
  }
  
  var ellipse = function(shape_data, fill_style, stroke_style, stroke_width) {
    fill_style = fill_style || '#FFFFFF';
    stroke_style = stroke_style || '#000000';
    stroke_width = stroke_width || 0;
    var ctx = my.context; // shorthand
    ctx.save();
    ctx.fillStyle = fill_style;
    ctx.strokeStyle = stroke_style;
    ctx.save();
    ctx.translate(shape_data.cx, shape_data.cy);
    ctx.scale(shape_data.rx, shape_data.ry);
    ctx.beginPath();
    ctx.arc(0, 0, 1, 0, 2*Math.PI, false);
    ctx.fill();
    ctx.restore();
    ctx.lineWidth = stroke_width;
    ctx.stroke();
    ctx.restore();
  };
  pub.ellipse = ellipse;
  
  var circle = function(shape_data, fill_style, stroke_style, stroke_width) {
    var edata = {
      cx:shape_data.cx, cy:shape_data.cy, rx:shape_data.r, ry:shape_data.r};
    return ellipse(edata,fill_style, stroke_style, stroke_width);
  };
  pub.circle = circle;

  var clear = function() {
    my.context.clearRect(0, 0, my.canvas.width, my.canvas.height);
  }
  pub.clear = clear;

  return pub;
};

// Colors from www.ColorBrewer.org by Cynthia A. Brewer, Geography, 
// Pennsylvania State University.
// 
// These are organized by:
// Name : [two arrays of three colors each in rgb format]
// Each array is arranged from darkest to lightest.
var color_schemes = {
  'pu_or': {
    'group_0': '241, 163, 64',
    'group_1': '152, 142, 195',
    'group_2': '166, 219, 160',
    'aoi': '166, 219, 160',
    'highlight': '179, 88, 6',
  },
    
  'category_1' : {
    'group_0': '228, 26, 28',
    'group_1': '55, 126, 184',
    'group_2': '152, 78, 163',
    'aoi': '152, 78, 163',
    'highlight': '77, 175, 74',
  },
  
  'category_2' : {
    'group_0': '31, 120, 180',
    'group_1': '51, 160, 44',
    'group_2': '253, 191, 111',
    'aoi': '253, 191, 111',
    'highlight': '227, 26, 28',
  }
};