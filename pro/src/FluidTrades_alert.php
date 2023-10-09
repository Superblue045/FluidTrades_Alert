<?php
require '../vendor/autoload.php';

// Function to get the top 200 list
function getTopList($api_key) {
    $url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest';
    $parameters = [
        'start' => '1',
        'limit' => '100',
        'sort' => 'market_cap',
        'convert' => 'USD',
    ];
    $headers = [
        'Accepts: application/json',
        'X-CMC_PRO_API_KEY: ' . $api_key,
    ];

    $ch = curl_init($url . '?' . http_build_query($parameters));
    curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

    $response = curl_exec($ch);
    curl_close($ch);

    $data = json_decode($response, true);

    if (isset($data['status']['error_code']) && $data['status']['error_code'] === 0) {
        return $data['data'];
    } else {
        $error_message = $data['status']['error_message'];
        throw new Exception("API request failed. Error: $error_message");
    }
}

// Function to get OHLC data using MEXC API
function getOHLCData($symbol, $timeframe) {
    $base_url = "https://www.mexc.com/open/api/v2/market/kline?symbol={$symbol}_USDT&interval={$timeframe}m&limit=50";

    $ch = curl_init($base_url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

    $response = curl_exec($ch);
    $http_status_code = curl_getinfo($ch, CURLINFO_HTTP_CODE); // Get the HTTP status code
    curl_close($ch);

    if ($http_status_code === 200) {
        $all_data = json_decode($response, true);
        $ohlc_data_list = [];

        foreach ($all_data['data'] as $item) {
            $timestamp = $item[0];
            $timestamp_datetime = date('Y-m-d H:i:s', $timestamp);
            $close_price = (float) $item[2];
            $high_price = (float) $item[3];
            $low_price = (float) $item[4];

            $ohlc_data_list[] = [$timestamp_datetime, $high_price, $low_price, $close_price];
        }

        return $ohlc_data_list;
    } else {
        return ['error' => 'API request failed with status code: ' . $http_status_code];
    }
}


// API key
$api_key = '37b4a617-9609-48c6-8a41-d48db5b2ed44';

try {
    $telegram = new \TelegramBot\Api\BotApi('6349402772:AAHU4nMst0YFEyoxaogG5Nmnh8Q_kCQa9qY');
    function send_telegram_message($chatId, $message)
    {
        global $telegram;
        $telegram->sendMessage($chatId, $message, 'HTML');
    }
    $chatId = '5629632710';
    $message = "";

    $top_list = getTopList($api_key);

    foreach ($top_list as $currency) {
        $symbol = $currency['symbol'];
        $timeframe = '15';

        // foreach ($timeframes as $timeframe) {

        // }

        $time_ohlc_list = getOHLCData($symbol, $timeframe);

        $date_list = [];
        $close_price_list = [];

        if ($time_ohlc_list){
            foreach ($time_ohlc_list as $time_ohlc) {
                $Date = $time_ohlc[0];
                $close_price = $time_ohlc[3];
                $date_list[] = $Date;
                $close_price_list[] = $close_price;
            }
    
            //price data
            $data = [
                'Date' => $date_list,
                'Close' => $close_price_list,
            ];

            // Identify potential supply and demand zones
            $minCloseIndex = array_search(min($close_price_list), $close_price_list);
            $demand_zone = [$minCloseIndex, min($close_price_list)];
    
            $maxCloseIndex = array_search(max($close_price_list), $close_price_list);
            $supply_zone = [$maxCloseIndex, max($close_price_list)];
    
            $current_price = end($close_price_list);
            $demand_price = $demand_zone[1];
            $supply_price = $supply_zone[1];

            // var_dump($current_price, $supply_price,$demand_price  );
    
            if ($current_price >= $supply_price && count($close_price_list)!=1) {
                echo "{$symbol}: current_price: {$current_price}, supply_price: {$supply_price}\n";
                $message .= "<b>" . "+" . $symbol . ": supplyZone" . "</b>";
                $message.=chr(10);
            }else if ($current_price <= $demand_price && count($close_price_list)!=1) {
                echo "{$symbol}: current_price: {$current_price}, supply_price: {$demand_price}\n";
                $message .= "<b>" . "-" . $symbol . ": demandZone" . "</b>";
                $message.=chr(10);
            } else {
                echo "{$symbol}: current_price: {$current_price} is not in any zone.\n";
            }            
        } else {
            echo "No OHLC data available for this symbol." . PHP_EOL;
        }
    }
    if (!empty($message)) {
        send_telegram_message($chatId, $message);
        var_dump($message);
    }
} catch (Exception $e) {
    echo $e->getMessage();
}

?>
