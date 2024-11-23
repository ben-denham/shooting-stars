import { Meteor } from 'meteor/meteor';
import { check } from 'meteor/check';

import { PresenceCollection } from '/imports/db/PresenceCollection';

Meteor.publish('presence', function publishPresence(token) {
  check(token, String);
  if (!(Meteor.settings.presenceControllerTokensToConfig.hasOwnProperty(token))) {
    // Unrecognised tokens should be returned no data.
    return this.ready();
  }

  const thisTokenId = Meteor.settings.presenceControllerTokensToConfig[token].id;

  return PresenceCollection.find(
    {
      // Don't return the presence data for the client's own token.
      id: { $ne: thisTokenId },
    },
    {
      fields: {
        key: 1,
        id: 1,
        config: 1,
        presenceEvents: 1,
      }
    },
  );
});
