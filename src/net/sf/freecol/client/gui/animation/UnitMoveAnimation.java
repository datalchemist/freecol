/**
 *  Copyright (C) 2002-2024   The FreeCol Team
 *
 *  This file is part of FreeCol.
 *
 *  FreeCol is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  FreeCol is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with FreeCol.  If not, see <http://www.gnu.org/licenses/>.
 */

package net.sf.freecol.client.gui.animation;

import static net.sf.freecol.common.util.CollectionUtils.makeUnmodifiableList;
import static net.sf.freecol.common.util.Utils.delay;
import static net.sf.freecol.common.util.Utils.now;

import java.awt.Point;

import javax.swing.JLabel;

import net.sf.freecol.common.model.Tile;
import net.sf.freecol.common.model.Unit;


/**
 * Class for the animation of units movement.
 *
 * Uses time-based interpolation to ensure the animation takes a
 * consistent duration regardless of tile size or zoom level.
 */
final class UnitMoveAnimation extends Animation {

    /**
     * Display delay between one frame and another, in milliseconds.
     * 33ms == 30 fps
     */
    private static final long ANIMATION_DELAY = 33L;

    /** The animation speed client option. */
    private final int speed;


    /**
     * Build a new movement animation.
     *
     * @param unit The {@code Unit} to be animated.
     * @param sourceTile The {@code Tile} the unit is moving from.
     * @param destinationTile The {@code Tile} the unit is moving to.
     * @param speed The animation speed.
     * @param scale The scale factor for the unit image.
     */
    public UnitMoveAnimation(Unit unit,
                             Tile sourceTile, Tile destinationTile,
                             int speed, float scale) {
        super(unit, makeUnmodifiableList(sourceTile, destinationTile));

        this.speed = speed;
    }


    /**
     * Get the total animation duration for a given speed setting.
     *
     * @param speed The animation speed (1=slow, 2=normal, 3=fast).
     * @return The duration in milliseconds.
     */
    static long getDuration(int speed) {
        switch (speed) {
        case 1:  return 2000L;
        case 2:  return 1500L;
        case 3:  return 1000L;
        default: return 1500L;
        }
    }


    // Implement Animation

    /**
     * {@inheritDoc}
     */
    @Override
    public void executeWithLabel(JLabel unitLabel,
                                 Animations.Procedure paintCallback) {
        final Point srcPoint = this.points.get(0);
        final Point dstPoint = this.points.get(1);
        final long duration = getDuration(this.speed);
        final int dx = dstPoint.x - srcPoint.x;
        final int dy = dstPoint.y - srcPoint.y;

        final long startTime = now();
        for (;;) {
            long currentTime = now();
            double t = Math.min(1.0,
                (double)(currentTime - startTime) / duration);

            unitLabel.setLocation(srcPoint.x + (int)(t * dx),
                                  srcPoint.y + (int)(t * dy));
            paintCallback.execute();

            if (t >= 1.0) break;

            long frameEnd = now();
            long waitTime = ANIMATION_DELAY - (frameEnd - currentTime);
            if (waitTime > 0) {
                delay(waitTime, "Animation interrupted.");
            }
        }
    }
}
