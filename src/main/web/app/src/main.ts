import {autoinject, Bootstrap, Controller} from 'ng-right';

/**
 * @author john
 * @version 10/5/15 5:02 PM
 */
import './css/app.css';

import './vendor';

import app from './app';


@Bootstrap({
    module: app
})
@Controller('App')
export class App {

    private please;

    constructor() {
        this.please = 'yeah';
    }
}
