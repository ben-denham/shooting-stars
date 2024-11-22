import { Meteor } from 'meteor/meteor';

import { PaintCollection } from '/imports/db/PaintCollection';

Meteor.publish('paint', async function publishPaint() {
  return await PaintCollection.findAsync({}, {
    fields: {
      key: 1,
      painterMovements: 1,
    }
  });
});
