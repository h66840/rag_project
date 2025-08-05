import "jsr:@supabase/functions-js/edge-runtime.d.ts";

interface DeliveryUpdate {
  orderId: string;
  status: string;
  location: string;
  timestamp: string;
  estimatedDelivery?: string;
}

Deno.serve(async (req: Request) => {
  try {
    if (req.method !== 'POST') {
      return new Response(
        JSON.stringify({ error: 'Method not allowed' }),
        { status: 405, headers: { 'Content-Type': 'application/json' } }
      );
    }

    const deliveryUpdate: DeliveryUpdate = await req.json();
    
    // Validate required fields
    if (!deliveryUpdate.orderId || !deliveryUpdate.status || !deliveryUpdate.location) {
      return new Response(
        JSON.stringify({ error: 'Missing required fields: orderId, status, location' }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      );
    }

    // Real-time delivery tracking logic
    const trackingData = {
      orderId: deliveryUpdate.orderId,
      status: deliveryUpdate.status,
      currentLocation: deliveryUpdate.location,
      lastUpdated: deliveryUpdate.timestamp || new Date().toISOString(),
      estimatedDelivery: deliveryUpdate.estimatedDelivery,
      trackingHistory: []
    };

    // Simulate database update
    console.log('Updating delivery tracking:', trackingData);

    // Send real-time notification
    const response = {
      success: true,
      message: 'Delivery tracking updated successfully',
      data: trackingData
    };

    return new Response(
      JSON.stringify(response),
      {
        status: 200,
        headers: {
          'Content-Type': 'application/json',
          'Connection': 'keep-alive'
        }
      }
    );

  } catch (error) {
    console.error('Error in delivery tracking function:', error);
    
    return new Response(
      JSON.stringify({ 
        error: 'Internal server error',
        message: error.message 
      }),
      { 
        status: 500, 
        headers: { 'Content-Type': 'application/json' } 
      }
    );
  }
});