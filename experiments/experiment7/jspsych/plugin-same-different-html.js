var jsPsychSameDifferentHtml = (function (jspsych) {
  'use strict';

  const info = {
      name: "same-different-html",
      parameters: {
          /** Array containing the HTML content to be displayed. */
          stimuli: {
              type: jspsych.ParameterType.HTML_STRING,
              pretty_name: "Stimuli",
              default: undefined,
              array: true,
          },
          /** Correct answer: either "same" or "different". */
          answer: {
              type: jspsych.ParameterType.SELECT,
              pretty_name: "Answer",
              options: ["same", "different"],
              default: undefined,
          },
          /** The key that subjects should press to indicate that the two stimuli are the same. */
          same_key: {
              type: jspsych.ParameterType.KEY,
              pretty_name: "Same key",
              default: "q",
          },
          /** The key that subjects should press to indicate that the two stimuli are different. */
          different_key: {
              type: jspsych.ParameterType.KEY,
              pretty_name: "Different key",
              default: "p",
          },
          /** How long to show the first stimulus for in milliseconds. If null, then the stimulus will remain on the screen until any keypress is made. */
          first_stim_duration: {
              type: jspsych.ParameterType.INT,
              pretty_name: "First stimulus duration",
              default: 1000,
          },
          /** How long to show a blank screen in between the two stimuli. */
          gap_duration: {
              type: jspsych.ParameterType.INT,
              pretty_name: "Gap duration",
              default: 500,
          },
          /** How long to show the second stimulus for in milliseconds. If null, then the stimulus will remain on the screen until a valid response is made. */
          second_stim_duration: {
              type: jspsych.ParameterType.INT,
              pretty_name: "Second stimulus duration",
              default: 1000,
          },
          /** Any content here will be displayed below the stimulus. */
          prompt: {
              type: jspsych.ParameterType.HTML_STRING,
              pretty_name: "Prompt",
              default: null,
          },
      },
  };
  /**
   * **same-different-html**
   *
   * jsPsych plugin for showing two HTML stimuli sequentially and getting a same / different judgment via keypress
   *
   * @author Josh de Leeuw
   * @see {@link https://www.jspsych.org/plugins/jspsych-same-different-html/ same-different-html plugin documentation on jspsych.org}
   */
  class SameDifferentHtmlPlugin {
      constructor(jsPsych) {
          this.jsPsych = jsPsych;
      }
      trial(display_element, trial) {
          display_element.innerHTML =
              '<div class="jspsych-same-different-stimulus">' + trial.stimuli[0] + "</div>";
          var first_stim_info;
          if (trial.first_stim_duration > 0) {
              this.jsPsych.pluginAPI.setTimeout(function () {
                  showBlankScreen();
              }, trial.first_stim_duration);
          }
          else {
              const afterKeyboardResponse = (info) => {
                  first_stim_info = info;
                  showBlankScreen();
              };
              this.jsPsych.pluginAPI.getKeyboardResponse({
                  callback_function: afterKeyboardResponse,
                  valid_responses: "ALL_KEYS",
                  rt_method: "performance",
                  persist: false,
                  allow_held_key: false,
              });
          }
          const showBlankScreen = () => {
              display_element.innerHTML = "";
              this.jsPsych.pluginAPI.setTimeout(function () {
                  showSecondStim();
              }, trial.gap_duration);
          };
          const showSecondStim = () => {
              var html = '<div class="jspsych-same-different-stimulus">' + trial.stimuli[1] + "</div>";
              //show prompt here
              if (trial.prompt !== null) {
                  html += trial.prompt;
              }
              display_element.innerHTML = html;
              if (trial.second_stim_duration > 0) {
                  this.jsPsych.pluginAPI.setTimeout(function () {
                      display_element.querySelector(".jspsych-same-different-stimulus").style.visibility = "hidden";
                  }, trial.second_stim_duration);
              }
              const after_response = (info) => {
                  // kill any remaining setTimeout handlers
                  this.jsPsych.pluginAPI.clearAllTimeouts();
                  var correct = false;
                  var skey = trial.same_key;
                  var dkey = trial.different_key;
                  if (this.jsPsych.pluginAPI.compareKeys(info.key, skey) && trial.answer == "same") {
                      correct = true;
                  }
                  if (this.jsPsych.pluginAPI.compareKeys(info.key, dkey) && trial.answer == "different") {
                      correct = true;
                  }
                  var trial_data = {
                      rt: info.rt,
                      answer: trial.answer,
                      correct: correct,
                      stimulus: [trial.stimuli[0], trial.stimuli[1]],
                      response: info.key,
                  };
                  if (first_stim_info) {
                      trial_data["rt_stim1"] = first_stim_info.rt;
                      trial_data["response_stim1"] = first_stim_info.key;
                  }
                  display_element.innerHTML = "";
                  this.jsPsych.finishTrial(trial_data);
              };
              this.jsPsych.pluginAPI.getKeyboardResponse({
                  callback_function: after_response,
                  valid_responses: [trial.same_key, trial.different_key],
                  rt_method: "performance",
                  persist: false,
                  allow_held_key: false,
              });
          };
      }
  }
  SameDifferentHtmlPlugin.info = info;

  return SameDifferentHtmlPlugin;

})(jsPsychModule);
