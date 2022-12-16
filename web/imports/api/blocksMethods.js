import { Meteor } from 'meteor/meteor';
import { check, Match } from 'meteor/check';

import { BlocksStatesCollection } from '/imports/db/BlocksStatesCollection';
import { BlocksInputsCollection } from '/imports/db/BlocksInputsCollection';

export const INPUTS = [
  'left',
  'right',
  'rotate',
  'drop',
];

export const blocksMethods = {
  'blocks.sendInput'(inputType) {
    check(inputType, String);

    if (!INPUTS.includes(inputType)) {
      throw new Meteor.Error('invalid-input', 'Invalid input');
    }

    const selector = {key: 'inputs'};
    const oldRecord = BlocksInputsCollection.findOne(selector);
    // Keep any inputs younger than 5 seconds.
    const nowMs = Date.now();
    const keptInputs = oldRecord ? oldRecord.inputs.filter(input => input.timestamp >= nowMs - 5000) : [];

    BlocksInputsCollection.upsert(
      selector,
      {
        inputs: [...keptInputs, {type: inputType, timestamp: nowMs}],
        ...selector,
      }
    );
  },
  'blocks.updateState'(token, state) {
    check(token, String);
    check(state, {
      score: Number,
      playfield: [[Match.Integer]],
    });

    if (token != Meteor.settings.controllerToken) {
      throw new Meteor.Error('Invalid controller token');
    }

    const selector = {key: 'game-state'};
    const oldRecord = BlocksStatesCollection.findOne(selector);
    BlocksStatesCollection.upsert(
      selector,
      {
        ...state,
        highScore: Math.max((oldRecord?.highScore || 0), (state.score || 0)),
        ...selector,
      }
    );
  }
};

Meteor.methods(blocksMethods);
