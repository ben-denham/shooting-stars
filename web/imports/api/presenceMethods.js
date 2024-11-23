import { Meteor } from 'meteor/meteor';
import { check, Match } from 'meteor/check';

import { PresenceCollection } from '/imports/db/PresenceCollection';

const MAX_PRESENCE_SIZE = 50;
const MAX_PRESENCE_VALUE = 255;

export const presenceMethods = {
  async 'presence.getConfig'(token) {
    check(token, String);

    // Check token
    if (!(Meteor.settings.presenceControllerTokensToConfig.hasOwnProperty(token))) {
      throw new Meteor.Error('Invalid controller token');
    }
    const presenceConfig = Meteor.settings.presenceControllerTokensToConfig[token];

    return presenceConfig;
  },
  async 'presence.sendPresence'(token, presenceMap) {
    check(token, String);
    check(presenceMap, [[Match.Integer]]);

    // Check token
    if (!(Meteor.settings.presenceControllerTokensToConfig.hasOwnProperty(token))) {
      throw new Meteor.Error('Invalid controller token');
    }
    const presenceConfig = Meteor.settings.presenceControllerTokensToConfig[token];

    // Validation of presenceMap
    const outerLength = presenceMap.length;
    if (outerLength === 0) {
      throw new Meteor.Error('presenceMap must have at least one row');
    }
    if (outerLength > MAX_PRESENCE_SIZE) {
      throw new Meteor.Error(`presenceMap must have at most ${MAX_PRESENCE_SIZE} rows`);
    }
    const innerLength = presenceMap[0].length;
    if (innerLength === 0) {
      throw new Meteor.Error('presenceMap must have at least one column');
    }
    if (innerLength > MAX_PRESENCE_SIZE) {
      throw new Meteor.Error(`presenceMap must have at most ${MAX_PRESENCE_SIZE} columns`);
    }
    presenceMap.forEach(function (row) {
      if (row.length !== innerLength) {
        throw new Meteor.Error(`presenceMap rows must be the same length`);
      }
      if (row.some((value) => (value < 0) || (value > MAX_PRESENCE_VALUE))) {
        throw new Meteor.Error(`presenceMap values must be between 0 and ${MAX_PRESENCE_VALUE}`);
      }
    });

    const selector = {id: presenceConfig.id};
    const oldRecord = await PresenceCollection.findOneAsync(selector);
    const oldPresenceEvents = oldRecord ? oldRecord.presenceEvents: [];
    // Keep only the 10 most recent presenceEvents
    const keptPresenceEvents = oldPresenceEvents.sort((eventA, eventB) => eventA.timestamp - eventB.timestamp).slice(-10);
    await PresenceCollection.upsertAsync(
      selector,
      {
        ...selector,
        config: presenceConfig,
        presenceEvents: [
          ...keptPresenceEvents,
          {presenceMap: presenceMap, timestamp: (new Date()).getTime()},
        ],
      }
    );
  },
};

Meteor.methods(presenceMethods);
