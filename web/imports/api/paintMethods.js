import { Meteor } from 'meteor/meteor';
import { check, Match } from 'meteor/check';

import { PaintCollection } from '/imports/db/PaintCollection';

export const paintMethods = {
  async 'paint.sendMovement'(movement) {
    check(movement, {
      painterId: Match.Integer,
      colour: {hue: Number, saturation: Number},
      velocities: [{x: Number, y: Number, z: Number}],
    });
    const { painterId, colour, velocities } = movement;

    const nowMs = (new Date()).getTime();

    // Get current or default paint record.
    const selector = {key: 'paint'};
    const defaultRecord = {
      painterMovements: {},
      ...selector,
    };
    const record = await PaintCollection.findOneAsync(selector) || defaultRecord;

    // Add new movement.
    record.painterMovements[painterId] = record.painterMovements[painterId] || [];
    record.painterMovements[painterId].push({
      timestamp: nowMs,
      velocities: velocities,
      colour: colour,
    });

    const painterIds = Object.keys(record.painterMovements);
    // Keep a maximum of 10 movements per painter.
    painterIds.forEach((painterId) => {
      record.painterMovements[painterId] = record.painterMovements[painterId].slice(-10);
    });
    // Keep only the 10 most recently updated painters.
    const painterLastUpdated = (painterId) => (record.painterMovements[painterId][-1]?.timestamp || 0);
    const painterIdsToRemove = (
      painterIds
        .sort((painterIdA, painterIdB) => painterLastUpdated(painterIdA) - painterLastUpdated(painterIdB))
        .slice(10)
    );
    painterIdsToRemove.forEach((painterId) => {
      delete record.painterMovements[painterId];
    });

    await PaintCollection.upsertAsync(selector, record);
  },
};

Meteor.methods(paintMethods);
