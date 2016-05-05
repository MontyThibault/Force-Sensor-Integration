package forcePates;

import java.util.Arrays;

/**
 * Class that represents 1-4 force plates attached to a "LabPro"
 * @author chris
 */
public class ForcePlates {

    static {
    	System.loadLibrary("JavaDLL");
    }

    private float calibration[] = { 0.0f, 0.0f, 0.0f, 0.0f };
    private float forces[] = { 0.0f, 0.0f, 0.0f, 0.0f };
    
    /**
     * @return returns false if the device couldn't be opened. 
     */
    public native boolean openDevice();
    
    /**
     * Don't forget to add the \n at the end of every command. This function will not add it for you.
     * Also, the logger pro wont accept non-scientific notation for floats.
     * GOOD: 2.24810E+02
     * BAD: 224.810
     * @param s the string to send to the logger pro
     * @return true if the device gets the string, false otherwise.
     */
    public native boolean sendString(String s);
    
    /**
     * Don't use this command to get measurements from the labpro, only for debugging. 
     * @return The string that represents the bytes returned from the buffer in the labpro.
     */
    public native String getBytes();
    
    /**
     * Disconnect all the plates and the data collector. 
     * This function performs a cleanup and reset of the device first. 
     */
    public native void closeDevice();
    

    private native boolean getForces(float forces[]);
    
    /**
     * The forces will be calibrated if the calibration function was called.
     * @param plateForces an allocated array to hold the results.
     * @return true if the plateForces array was updated. 
     */
    public boolean update() {
        
        if(!getForces(this.forces))
        	return false;
        	
        if(this.calibration[0] == 0.0f) {
        	this.calibrate();
        }
        
        for(int i = 0; i < 4; i++) {
        	this.forces[i] -= this.calibration[i];
        }
        
        return true;
    }
    
    /**
     * This function samples data from the force plates and subtracts the calibration results from
     * all future samples. This function should only be called if this class is able to sample from
     * the force plates when this function is called. This function will run for 0.5 seconds. 
     */
    public void calibrate() {
    	this.calibration = this.forces.clone();
    }
    
    /**
     * Prints the current status of the logger pro.
     */
    public void printStatus() {
        if(sendString("s{7}\n"))
        {
            System.out.println(getBytes()); 
        }
        else
        {
            System.out.println("Couldn't request status.");
        }
    }
    
    @Override
    public String toString() {
    	return String.format("Calibration: %s\nForces: %s", Arrays.toString(this.calibration), Arrays.toString(this.forces));
    }
}
