import * as evolve from '../evolve';


test('main', async () => {
    const event = 'event';
    const context = 'context';
    const callback = (error, response) => {
	expect(response.statusCode).toEqual(200);
	expect(typeof response.body).toBe("string");
    };

    await evolve.main(event, context, callback);
});
