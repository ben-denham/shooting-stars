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
  async 'blocks.sendInput'(inputType) {
    check(inputType, String);

    if (!INPUTS.includes(inputType)) {
      throw new Meteor.Error('invalid-input', 'Invalid input');
    }

    const selector = {key: 'inputs'};
    const oldRecord = await BlocksInputsCollection.findOneAsync(selector);
    const oldInputs = oldRecord ? oldRecord.inputs : [];
    // Keep only the 10 most recent inputs
    const keptInputs = oldInputs.sort((inputA, inputB) => inputA.timestamp - inputB.timestamp).slice(-10);

    await BlocksInputsCollection.upsertAsync(
      selector,
      {
        inputs: [...keptInputs, {type: inputType, timestamp: (new Date()).getTime()}],
        ...selector,
      }
    );
  },
  async 'blocks.updateState'(token, state) {
    check(token, String);
    check(state, {
      score: Number,
      playfield: [[Match.Integer]],
      aiMode: Boolean,
    });

    if (!(Meteor.settings.blocksControllerTokens.includes(token))) {
      throw new Meteor.Error('Invalid controller token');
    }

    const selector = {key: 'game-state'};
    const oldRecord = await BlocksStatesCollection.findOneAsync(selector);
    await BlocksStatesCollection.upsertAsync(
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
