import { Meteor } from 'meteor/meteor';
import { BlocksStatesCollection } from '/imports/db/BlocksStatesCollection';
import { BlocksInputsCollection } from '/imports/db/BlocksInputsCollection';

Meteor.publish('blocksInputs', function publishBlocksInputs() {
  return BlocksInputsCollection.find({}, {
    fields: {
      key: 1,
      inputs: 1,
    }
  });
});

Meteor.publish('blocksStates', function publishBlocksStates() {
  return BlocksStatesCollection.find({}, {
    fields: {
      key: 1,
      playfield: 1,
      score: 1,
      highScore: 1,
    }
  });
});
