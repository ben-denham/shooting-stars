import { Meteor } from 'meteor/meteor';
import { BlocksStatesCollection } from '/imports/db/BlocksStatesCollection';
import { BlocksInputsCollection } from '/imports/db/BlocksInputsCollection';

Meteor.publish('blocksInputs', async function publishBlocksInputs() {
  return await BlocksInputsCollection.findAsync({}, {
    fields: {
      key: 1,
      inputs: 1,
    }
  });
});

Meteor.publish('blocksStates', async function publishBlocksStates() {
  return await BlocksStatesCollection.findAsync({}, {
    fields: {
      key: 1,
      playfield: 1,
      aiMode: 1,
      score: 1,
      highScore: 1,
    }
  });
});
