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

package net.sf.freecol.client.gui;

import java.awt.event.MouseWheelEvent;
import java.awt.event.MouseWheelListener;

import net.sf.freecol.client.FreeColClient;
import net.sf.freecol.client.control.FreeColClientHolder;


/**
 * Listens to the mouse wheel at the level of the Canvas to zoom the main map.
 */
public final class CanvasMouseWheelListener extends FreeColClientHolder
        implements MouseWheelListener {


    /**
     * Creates a new mouse wheel listener.
     *
     * @param freeColClient The enclosing {@code FreeColClient}.
     */
    public CanvasMouseWheelListener(FreeColClient freeColClient) {
        super(freeColClient);
    }


    // Interface MouseWheelListener

    /**
     * {@inheritDoc}
     */
    @Override
    public void mouseWheelMoved(MouseWheelEvent e) {
        if (!e.getComponent().isEnabled()) return;

        final GUI gui = getGUI();
        if (e.getWheelRotation() < 0) {
            if (gui.canZoomInMap()) {
                gui.zoomInMap();
            }
        } else {
            if (gui.canZoomOutMap()) {
                gui.zoomOutMap();
            }
        }
    }
}
