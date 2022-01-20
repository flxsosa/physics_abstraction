var jsPsychReconstruction = (function (jspsych) {
  'use strict';

  const info = {
      name: "reconstruction",
      parameters: {
          /** A function with a single parameter that returns an HTML-formatted string representing the stimulus. */
          stim_function: {
              type: jspsych.ParameterType.FUNCTION,
              pretty_name: "Stimulus function",
              default: undefined,
          },
          /** The starting value of the stimulus parameter. */
          starting_value: {
              type: jspsych.ParameterType.FLOAT,
              pretty_name: "Starting value",
              default: 0.5,
          },
          /** The change in the stimulus parameter caused by pressing one of the modification keys. */
          step_size: {
              type: jspsych.ParameterType.FLOAT,
              pretty_name: "Step size",
              default: 0.05,
          },
          /** The key to press for increasing the parameter value. */
          key_increase: {
              type: jspsych.ParameterType.KEY,
              pretty_name: "Key increase",
              default: "h",
          },
          /** The key to press for decreasing the parameter value. */
          key_decrease: {
              type: jspsych.ParameterType.KEY,
              pretty_name: "Key decrease",
              default: "g",
          },
          /** The text that appears on the button to finish the trial. */
          button_label: {
              type: jspsych.ParameterType.STRING,
              pretty_name: "Button label",
              default: "Continue",
          },
      },
  };
  /**
   * **reconstruction**
   *
   * jsPsych plugin for a reconstruction task where the subject recreates a stimulus from memory
   *
   * @author Josh de Leeuw
   * @see {@link https://www.jspsych.org/plugins/jspsych-reconstruction/ reconstruction plugin documentation on jspsych.org}
   */
  class ReconstructionPlugin {
      constructor(jsPsych) {
          this.jsPsych = jsPsych;
      }
      trial(display_element, trial) {
          // current param level
          var param = trial.starting_value;
          const endTrial = () => {
              // measure response time
              var endTime = performance.now();
              var response_time = Math.round(endTime - startTime);
              // clear keyboard response
              this.jsPsych.pluginAPI.cancelKeyboardResponse(key_listener);
              // save data
              var trial_data = {
                  rt: response_time,
                  final_value: param,
                  start_value: trial.starting_value,
              };
              display_element.innerHTML = "";
              // next trial
              this.jsPsych.finishTrial(trial_data);
          };
          const draw = (param) => {
              //console.log(param);
              display_element.innerHTML =
                  '<div id="jspsych-reconstruction-stim-container">' + trial.stim_function(param) + "</div>";
              // add submit button
              display_element.innerHTML +=
                  '<button id="jspsych-reconstruction-next" class="jspsych-btn jspsych-reconstruction">' +
                      trial.button_label +
                      "</button>";
              display_element
                  .querySelector("#jspsych-reconstruction-next")
                  .addEventListener("click", endTrial);
          };
          // set-up key listeners
          const after_response = (info) => {
              //console.log('fire');
              var key_i = trial.key_increase;
              var key_d = trial.key_decrease;
              // get new param value
              if (this.jsPsych.pluginAPI.compareKeys(info.key, key_i)) {
                  param = param + trial.step_size;
              }
              else if (this.jsPsych.pluginAPI.compareKeys(info.key, key_d)) {
                  param = param - trial.step_size;
              }
              param = Math.max(Math.min(1, param), 0);
              // refresh the display
              draw(param);
          };
          // listen for responses
          var key_listener = this.jsPsych.pluginAPI.getKeyboardResponse({
              callback_function: after_response,
              valid_responses: [trial.key_increase, trial.key_decrease],
              rt_method: "performance",
              persist: true,
              allow_held_key: true,
          });
          // draw first iteration
          draw(param);
          var startTime = performance.now();
      }
  }
  ReconstructionPlugin.info = info;

  return ReconstructionPlugin;

})(jsPsychModule);
