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
    const oldInputs = oldRecord ? oldRecord.inputs : [];
    // Keep only the 10 most recent inputs
    const keptInputs = oldInputs.sort((inputA, inputB) => inputA.timestamp - inputB.timestamp).slice(-10);

    BlocksInputsCollection.upsert(
      selector,
      {
        inputs: [...keptInputs, {type: inputType, timestamp: (new Date()).getTime()}],
        ...selector,
      }
    );
  },
  'blocks.updateState'(token, state) {
    check(token, String);
    check(state, {
      score: Number,
      playfield: [[Match.Integer]],
      aiMode: Boolean,
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
        timestamp: (new Date()).getTime(),
        ...selector,
      }
    );
  }
};

Meteor.methods(blocksMethods);
