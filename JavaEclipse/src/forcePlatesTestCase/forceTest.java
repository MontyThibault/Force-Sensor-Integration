/**
 * 
 */
package forcePlatesTestCase;

import java.io.DataInputStream;
import java.io.IOException;

import forcePates.ForcePlates;

/**
 * @author chris
 */
public class forceTest {

    /**
     * gdfs
     */
    static ForcePlates plates;
    
    /**
     * @param args
     */
    public static void main(String[] args) {
        plates = new ForcePlates();
        if(!plates.openDevice())
        {
            System.out.println("Couldn't open the force plates.");
            System.exit(1);
        }
        System.out.println("Plates are open!");
        if(!plates.sendString("s{7}\n"))
            System.out.println("Couldn't send a string!");
        
        //System.out.println(plates.getBytes());
        
        if(!plates.sendString("s{1, 1, 14, 0, 0, 1}\n"))
            System.out.println("Couldn't send a string!");
        if(!plates.sendString("s{4, 1, 1, 1, -2.24810E+02, 2.24810E+02}\n"))
            System.out.println("Couldn't send a string!");
        if(!plates.sendString("s{1, 2, 14, 0, 0, 1}\n"))
            System.out.println("Couldn't send a string!");
        if(!plates.sendString("s{4, 2, 1, 1, -2.24810E+02, 2.24810E+02}\n"))
            System.out.println("Couldn't send a string!");
        if(!plates.sendString("s{1, 3, 14, 0, 0, 1}\n"))
            System.out.println("Couldn't send a string!");
        if(!plates.sendString("s{4, 3, 1, 1, -2.24810E+02, 2.24810E+02}\n"))
            System.out.println("Couldn't send a string!");
        if(!plates.sendString("s{1, 4, 14, 0, 0, 1}\n"))
            System.out.println("Couldn't send a string!");
        if(!plates.sendString("s{4, 4, 1, 1, -2.24810E+02, 2.24810E+02}\n"))
            System.out.println("Couldn't send a string!");
        if(!plates.sendString("s{3, 0.5, -1, 0, 0, 0, 0, 0, 0, 0, 0}\n"))
            System.out.println("Couldn't send a string!");
        if(!plates.sendString("s{7}\n"))
            System.out.println("Couldn't send a string!");
        
        
        System.out.println(plates.getBytes());
        float forceData[] = new float[4];
        DataInputStream dis = new DataInputStream(System.in) ;

        try {
            while(dis.available() == 0) {
                Thread.sleep(500);
                
                plates.update();
                System.out.println(plates);
            }
        } catch(IOException excep) {
            System.out.println("Caught an exception (IO)");
        } catch(java.lang.InterruptedException excep) {
            System.out.println("Caught an exception (InterruptedException)");
        }
        
        System.out.println("Key pressed exiting.");
        plates.closeDevice();
    }
}
