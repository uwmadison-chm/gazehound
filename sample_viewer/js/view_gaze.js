// A class that handles playing eyetracking data
var gaze_viewer = function(spec) {
  var pub = this;   // public stuff
  var my = {};      // private stuff
  spec = spec || {};
  
  my.point_index = 0;
  my.playing = false;
  my.view_data = spec.view_data;
  my.canvas = $(spec.canvas);
  my.context = my.canvas.getContext('2d');
  my.renderer = eyetrack_renderer({'canvas': my.canvas});
  my.controls_conatiner = $(spec.control_element);
  my.nav_container = $(spec.nav_container);
  my.stim_element = $(spec.stim_element);
  my.stim_img_prefix = spec.stim_img_prefix || '';
  my.thumb_prefix = spec.thumb_prefix || '';
  my.pp_button = $(spec.pp_button);
  my.fps = spec.fps;
  my.time_container = $(spec.time_container);
  my.prog_element = my.time_container.down(".first");
  my.len_element = my.time_container.down(".second");
  my.schedule_ms = (1000/my.fps);
  my.playback_speed = 1;
  my.speed_control = $(spec.speed_control);
  my.point_index_offset = 0;
  
  var play = function(from_start) {
    my.play_started_at = new Date();
    my.rendered_count = 0;
    
    if (from_start || my.point_index >= (my.gaze_len-1)) {
      my.point_index = 0;
      my.point_index_offset = 0;
    }
    my.playing = true;
    render_and_schedule();
  };
  pub.play = play;
  var pause = function() {};
  pub.pause = pause;
  
  var set_stim_image = function(stim_name) {
    var pfx = my.stim_img_prefix+"/";
    my.stim_element.src = pfx+my.view_data.stim_images[stim_name];
  }

  var set_stim_index = function(idx) {
    my.stim_index = idx;
    select_nav_element(my.nav_array[idx]);
    my.stim_name = my.view_data.stims[idx];
    set_stim_image(my.stim_name);
    my.renderer.clear();
    my.stim_data = my.view_data.viewdata[my.stim_name];
    my.point_index = 0;
    my.gaze_len = gaze_len();
    update_time_len();
  }
  pub.set_stim_index = set_stim_index;
  
  // Todo, if we need this a lot: memoize!
  var gaze_len = function() {
    var max = 0;
    for (sname in my.stim_data) {
      var view_arrays = my.stim_data[sname];
      for (var i = 0; i < view_arrays.length; i++) {
        if (view_arrays[i].length > max) {
          max = view_arrays[i].length
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
      my.playing = false;
    }
    if (my.playing) {
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
    my.len_element.update(len_sec.toFixed(3));
  }
  
  var update_time_progress = function() {
    var cur_sec = (my.point_index / my.view_data.samples_per_second);
    my.prog_element.update(cur_sec.toFixed(3));
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
    for (sname in my.stim_data) {
      var view_arrays = my.stim_data[sname];
      for (var i = 0; i < view_arrays.length; i++) {
        var p = view_arrays[i][my.point_index];
        if (p) {
          my.renderer.circle({cx:p[0], cy:p[1], r:1});
        }
      }
    }
  }
  
  var build_nav = function() {
    // Hold on to these, so we can select an element in set_stim_index()
    my.nav_array = new Array(); 
    my.nav_container.update("");
    for (var i = 0; i < my.view_data.stims.length; i++) {
      var li = nav_li(i);
      my.nav_array[i] = li;
      my.nav_container.insert(li);
    }
  }
  
  var select_nav_element = function(elt) {
    elt.adjacent(".selected").invoke("removeClassName", "selected");
    elt.addClassName("selected");
  }
  
  // Creates a <li> for the navigation, and makes it watch for clicks.
  var nav_li = function(stim_idx) {
    var stim_name = my.view_data.stims[stim_idx]
    var li = new Element("li", {"class": "clearfix"});
    var thumb_path = my.thumb_prefix+"/"+my.view_data.stim_images[stim_name];
    li.insert(new Element("img", {"src": thumb_path}));
    li.insert(new Element("div").update(my.view_data.stims[stim_idx]));
    li.observe('click', function(idx) {
      return function(event) {
        set_stim_index(idx);
      };
    }(stim_idx));
    return li;
  }
  
  var set_play_pause = function() {
    if (my.playing) {
      my.pp_button.update("Pause");
    } else {
      my.pp_button.update("Play");
    }
  }
  
  // Event-handling functions
  var handle_play_pause_click = function(event) {
    my.playing = !my.playing;
    set_play_pause();
    if (my.playing) {
      play();
    }
  }
  my.pp_button.observe("click", handle_play_pause_click);
  
  var handle_speed_change = function(event) {
    my.playback_speed = parseFloat($(this).getValue());
  }
  my.speed_control.observe('change', handle_speed_change);
  
  build_nav();
  set_stim_index(0);
  
  var debug = function() {
    return my;
  }
  pub.debug = debug;
  
  console.log(my);
  return pub;
  
  
}

var eyetrack_renderer = function(spec) {
  var pub = this;   // public things
  var my = {};      // private things
  spec = spec || {};

  my.canvas = $(spec.canvas);
  my.context = my.canvas.getContext('2d');
  
  var ellipse = function(shape_data, fill_style, stroke_style) {
    var ctx = my.context; // shorthand
    ctx.save();
    ctx.save();
    ctx.translate(shape_data.cx, shape_data.cy);
    ctx.scale(shape_data.rx, shape_data.ry);
    ctx.beginPath();
    ctx.arc(0, 0, 1, 0, 2*Math.PI, false);
    ctx.fill();
    ctx.restore();
    ctx.lineWidth=2;
    ctx.stroke();
    ctx.restore();
  };
  pub.ellipse = ellipse;
  
  var circle = function(shape_data, fill_style, stroke_style) {
    var edata = {
      cx:shape_data.cx, cy:shape_data.cy, rx:shape_data.r, ry:shape_data.r};
    return ellipse(edata,fill_style, stroke_style);
  };
  pub.circle = circle;

  var clear = function() {
    my.context.clearRect(0, 0, my.canvas.width, my.canvas.height);
  }
  pub.clear = clear;

  return pub;
};