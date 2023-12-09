import { Meteor } from 'meteor/meteor';

import { PaintCollection } from '/imports/db/PaintCollection';

Meteor.publish('paint', function publishPaint() {
  return PaintCollection.find({}, {
    fields: {
      key: 1,
      painterMovements: 1,
    }
  });
});
